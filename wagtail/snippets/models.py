from functools import lru_cache

from django.contrib.admin.utils import quote
from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS
from django.urls import reverse
from django.utils.module_loading import import_string

from wagtail.admin.viewsets import viewsets
from wagtail.hooks import search_for_hooks
from wagtail.models import DraftStateMixin, LockableMixin, WorkflowMixin

SNIPPET_MODELS = []


# register_snippet will often be called before models are fully loaded, which may cause
# issues with constructing viewsets (https://github.com/wagtail/wagtail/issues/9586).
# We therefore initially set a DEFER_REGISTRATION flag to indicate that registration
# should not be processed immediately, but added to the DEFERRED_REGISTRATIONS list to be
# handled later. This is initiated from WagtailSnippetsAppConfig.ready(), at which point
# we can be sure that models are fully loaded.
DEFER_REGISTRATION = True
DEFERRED_REGISTRATIONS = []


def get_snippet_models():
    # Snippets can be registered in wagtail_hooks.py by calling register_snippet
    # as a function instead of a decorator. Make sure we search for hooks before
    # returning the list of snippet models.
    search_for_hooks()
    return SNIPPET_MODELS


@lru_cache(maxsize=None)
def get_workflow_enabled_models():
    return [model for model in get_snippet_models() if issubclass(model, WorkflowMixin)]


def get_editable_models(user):
    from wagtail.snippets.permissions import get_permission_name

    return [
        model
        for model in get_snippet_models()
        if user.has_perm(get_permission_name("change", model))
    ]


class SnippetAdminURLFinder:
    # subclasses should define a 'model' attribute
    def __init__(self, user=None):
        if user:
            from wagtail.snippets.permissions import get_permission_name

            self.user_can_edit = user.has_perm(
                get_permission_name("change", self.model)
            )
        else:
            # skip permission checks
            self.user_can_edit = True

    def get_edit_url(self, instance):
        if self.user_can_edit:
            return reverse(
                instance.snippet_viewset.get_url_name("edit"),
                args=[quote(instance.pk)],
            )


def register_snippet(model, viewset=None):
    if DEFER_REGISTRATION:
        # Models may not have been fully loaded yet, so defer registration until they are -
        # add it to the list of registrations to be processed by register_deferred_snippets
        DEFERRED_REGISTRATIONS.append((model, viewset))
    else:
        _register_snippet_immediately(model, viewset)

    return model


def _register_snippet_immediately(model, viewset=None):
    # Register the viewset and formfield for this snippet model,
    # skipping the check for whether models are loaded

    if model in SNIPPET_MODELS:
        # Do not create duplicate registrations of the same model
        return

    from wagtail.snippets.views.snippets import SnippetViewSet

    if viewset is None:
        viewset = SnippetViewSet
    elif isinstance(viewset, str):
        viewset = import_string(viewset)

    admin_viewset = viewset(model)
    viewsets.register(admin_viewset)
    model.snippet_viewset = admin_viewset

    SNIPPET_MODELS.append(model)
    SNIPPET_MODELS.sort(key=lambda x: x._meta.verbose_name)


def register_deferred_snippets():
    """
    Called from WagtailSnippetsAppConfig.ready(), at which point we can be sure all models
    have been loaded and register_snippet can safely construct viewsets.
    """
    global DEFER_REGISTRATION
    DEFER_REGISTRATION = False
    for model, viewset in DEFERRED_REGISTRATIONS:
        _register_snippet_immediately(model, viewset)


def create_extra_permissions(*args, using=DEFAULT_DB_ALIAS, **kwargs):
    def get_permission(model, content_type, name):
        return Permission(
            content_type=content_type,
            codename=get_permission_codename(name, model._meta),
            name=f"Can {name} {model._meta.verbose_name_raw}",
        )

    model_cts = ContentType.objects.get_for_models(
        *get_snippet_models(), for_concrete_models=False
    )

    permissions = []
    for model, ct in model_cts.items():
        if issubclass(model, DraftStateMixin):
            permissions.append(get_permission(model, ct, "publish"))
        if issubclass(model, LockableMixin):
            permissions.append(get_permission(model, ct, "lock"))
            permissions.append(get_permission(model, ct, "unlock"))

    # Use bulk_create with ignore_conflicts instead of checking for existence
    # prior to creation to avoid additional database query.
    Permission.objects.using(using).bulk_create(permissions, ignore_conflicts=True)

import { Controller } from '@hotwired/stimulus';

/**
 *
 * @example
 * <section
 * data-controller="w-panel"
 * data-action="w-panel:toggle->w-panel#toggle"
 * >
 *   <div>
 *       <a data-w-panel-target="anchor">
 *       </a>
 *       <button data-action="w-panel->toggle">
 *       </button>
 *           <h2 data-w-panel-target="heading">
 *                   <span data-w-panel-target="heading-text"></span>
 *           </h2>
 *           <div data-w-panel-target="controls">
 *           </div>
 *   </div>
 *   <div
 * data-w-panel-target="content"
 * data-action="beforematch->w-panel#toggle"
 * >
 *   </div>
 * </section>
 * */
export class PanelController extends Controller<HTMLElement> {

    static targets = ['anchor', 'content', 'heading', 'headingText', 'controls'];
    
    declare readonly anchorTarget: HTMLElement;
    declare readonly contentTarget: HTMLElement;
    declare readonly headingTarget: HTMLElement;
    declare readonly headingTextTarget: HTMLElement;
    declare readonly controlsTarget: HTMLElement;
    
    declare readonly hasAnchorTarget: boolean;
    declare readonly hasContentTarget: boolean;
    declare readonly hasHeadingTarget: boolean;
    declare readonly hasHeadingTextTarget: boolean;
    declare readonly hasControlsTarget: boolean;
    
    // declare readonly isExpanded: boolean;
    
    toggle() {
        if (this.isExpanded) {
        this.collapse();
        } else {
        this.expand();
        }
    }
    
    expand() {
        if (this.isExpanded) return;
    
        this.contentTarget.hidden = false;
        this.anchorTarget.setAttribute('aria-expanded', 'true');
        this.headingTarget.setAttribute('aria-expanded', 'true');
        this.headingTextTarget.setAttribute('aria-expanded', 'true');
        this.controlsTarget.setAttribute('aria-expanded', 'true');
    }
    
    collapse() {
        if (!this.isExpanded) return;
    
        this.contentTarget.hidden = true;
        this.anchorTarget.setAttribute('aria-expanded', 'false');
        this.headingTarget.setAttribute('aria-expanded', 'false');
        this.headingTextTarget.setAttribute('aria-expanded', 'false');
        this.controlsTarget.setAttribute('aria-expanded', 'false');
    }
    
    get isExpanded() {
        return this.anchorTarget.getAttribute('aria-expanded') === 'true';
    }




}

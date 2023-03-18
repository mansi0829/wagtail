import { Application } from "@hotwired/stimulus";
import { PanelController } from "./PanelController";

jest.useFakeTimers();

describe('PanelController',()=>{
    let application;
    beforeEach(()=>{
        application?.stop();
        document.body.innerHTML = `
        <div
        class="panel"
        data-controller="w-panel"
        data-action="w-panel:toggle@document->w-panel#toggle"
        >
        <div data-w-panel-target="container"></div>
        <template data-w-panel-target="template">
            <div class="panel__content">
                <div class="panel__header">
                    <h2 class="panel__title">Panel title</h2>
                    <button class="panel__close" data-action="w-panel:toggle"></button>
                </div>
                <div class="panel__body">
                    <p>Panel content</p>
                </div>
            </div>
        </template>
        </div>
        `;
        application = Application.start();
        application.register('w-panel', PanelController);
    })
    it('should not add elements when connected by default',()=>{
        expect(document.querySelectorAll('div')).toHaveLength(0);
    })
    it('should allow for a panel to be added via the add method',()=>{
        const text = 'first panel text';
        document.dispatchEvent(
            new CustomEvent('w-panel:add',{detail:{text}})
        )
        const item = document.querySelector('div');
        expect(item.classList.toString()).toEqual('panel__content');
        expect(item.lastElementChild.textContent).toEqual(text);
    })
    it('should allow for a second panel to be added',async()=>{
        expect(document.querySelectorAll('div')).toHaveLength(1);
        const text = 'second panel text';
        document.dispatchEvent(
            new CustomEvent('w-panel:add',{detail:{text}})
        )
        const item = document.querySelector('div');
        expect(item.classList.toString()).toEqual('panel__content');
        expect(item.lastElementChild.textContent).toEqual(text);
    })
})


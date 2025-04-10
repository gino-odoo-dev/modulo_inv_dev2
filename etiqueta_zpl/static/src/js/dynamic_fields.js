/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { FormRenderer } from "@web/views/form/form_renderer";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { useRef, onMounted, onWillUpdateProps } = owl;

class DynamicFieldsRenderer extends FormRenderer {
    setup() {
        super.setup();
        this.root = useRef("root");
        
        onMounted(() => this.updateFieldVisibility());
        onWillUpdateProps(() => this.updateFieldVisibility());
    }

    updateFieldVisibility() {
        const formatValue = this.props.record.data.zpl_format;
        if (!formatValue || !this.root.el) return;

        this.root.el.querySelectorAll('.format_field').forEach(field => {
            const requiredFormats = field.dataset.format.split(' ');
            const shouldShow = requiredFormats.includes(formatValue);
            
            const widgetContainer = field.closest('.o_field_widget');
            if (widgetContainer) {
                widgetContainer.style.display = shouldShow ? '' : 'none';
                
                const label = widgetContainer.previousElementSibling;
                if (label && label.classList.contains('o_form_label')) {
                    label.style.display = shouldShow ? '' : 'none';
                }
            }
        });
    }
}

DynamicFieldsRenderer.components = { ...FormRenderer.components };

class DynamicFieldsController extends FormController {
    setup() {
        super.setup();
        this.rendererProps = {
            ...this.rendererProps,
            updateFieldVisibility: this._updateFieldVisibility.bind(this),
        };
    }

    _updateFieldVisibility() {
        if (this.renderer && this.renderer.updateFieldVisibility) {
            this.renderer.updateFieldVisibility();
        }
    }
}

registry.category("form_renderers").add("dynamic_fields_form", DynamicFieldsRenderer);
registry.category("form_controllers").add("dynamic_fields_form", DynamicFieldsController);
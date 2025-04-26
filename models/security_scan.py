from odoo import models, fields, api
from datetime import datetime
import logging
import os

_logger = logging.getLogger(__name__)

class SecurityScan(models.Model):
    _name = 'security.scan'
    _description = 'Security Scan'

    name = fields.Char(string='Scan Name', required=True, default=lambda self: self._default_name())
    scan_date = fields.Datetime(string='Scan Date', default=fields.Datetime.now)

    master_password_set = fields.Boolean(string='Master Password Set', default=True)
    https_enabled = fields.Boolean(string='HTTPS Enabled', default=True)
    access_rules_defined = fields.Boolean(string='Access Rules Defined', default=True)
    log_file_present = fields.Boolean(string='Log File Present', default=True)
    db_filter_set = fields.Boolean(string='DB Filter Set', default=True)
    db_listing_disabled = fields.Boolean(string='DB Listing Disabled', default=True)

    notes = fields.Html(string="Scan Results")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', default='draft', readonly=True)

    @api.model
    def _default_name(self):
        return f"Scan {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    def _check_master_password(self):
        try:
            self.env.cr.execute("SELECT count(*) FROM ir_config_parameter WHERE key='auth_master'")
            count = self.env.cr.fetchone()[0]
            return count > 0, f"Found {count} master password record(s)."
        except Exception as e:
            _logger.error("Error checking master password: %s", e)
            return False, str(e)

    def _check_https(self):
        try:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if base_url:
                if base_url.startswith('https://'):
                    return True, f"Base URL is secure: '{base_url}'"
                else:
                    return False, f"Base URL is not secure: '{base_url}'"
            return False, "Base URL not set."
        except Exception as e:
            _logger.error("Error checking HTTPS: %s", e)
            return False, str(e)

    def _check_log_file(self):
        try:
            # 1st attempt: config param
            log_level = self.env['ir.config_parameter'].sudo().get_param('logging_level')
            if log_level:
                return True, f"Log level set in database: '{log_level}'"

            # 2nd attempt: environment variable
            import os
            if os.environ.get('LOG_LEVEL'):
                return True, f"Log level set in environment: '{os.environ.get('LOG_LEVEL')}'"

            # 3rd attempt: Python logger
            root_logger_level = logging.getLogger().getEffectiveLevel()
            if root_logger_level:
                level_name = logging.getLevelName(root_logger_level)
                return True, f"Root logger level: '{level_name}'"

            return False, "Log level not detected in database, environment, or logger."
        except Exception as e:
            _logger.error("Error checking log file: %s", e)
            return False, str(e)

    def _check_db_filter(self):
        try:
            # dbfilter is usually stored in config, not DB
            dbfilter = self.env['ir.config_parameter'].sudo().get_param('dbfilter')
            if dbfilter:
                return True, f"Database filter set: '{dbfilter}'"
            return False, "No database filter set."
        except Exception as e:
            _logger.error("Error checking DB filter: %s", e)
            return False, str(e)

    def _check_db_listing(self):
        try:
            db_list_enabled = self.env['ir.config_parameter'].sudo().get_param('list_db')
            if db_list_enabled is not None:
                if isinstance(db_list_enabled, bool):
                    if not db_list_enabled:
                        # bool check
                        return True, "Database listing disabled."
                    else:
                        # bool check
                        return False, "Database listing still enabled."
                else:
                    # It was string, safe to lower()
                    if db_list_enabled.lower() in ['false', '0', 'no']:
                        # string check
                        return True, "Database listing disabled."
                    else:
                        return False, f"Database listing still enabled: '{db_list_enabled}'"
            return False, "Database listing status not found."
        except Exception as e:
            _logger.error("Error checking DB listing: %s", e)
            return False, str(e)

    def _check_access_rules(self):
        try:
            # Critical models that MUST have access rules
            whitelisted_models = [
                "mail.thread.cc",
                "mail.thread",
                "mail.thread.blacklist",
                "mail.thread.main.attachment",
                "mail.thread.phone",
                "account.chart.template",
                "account.move.send",
                "report.account.report_invoice",
                "report.account.report_invoice_with_payments",
                "mail.activity.mixin",
                "format.address.mixin",
                "analytic.mixin",
                "analytic.plan.fields.mixin",
                "account.edi.xml.ubl_a_nz",
                "web_editor.assets",
                "sequence.mixin",
                "avatar.mixin",
                "barcodes.barcode_events_mixin",
                "base",
                "account.edi.xml.ubl_de",
                "report.mrp.report_bom_structure",
                "bus.listener.mixin",
                "account.edi.common",
                "sale.edi.common",
                "format.vat.label.mixin",
                "account.edi.xml.ubl_efff",
                "mail.alias.mixin",
                "mail.alias.mixin.optional",
                "account.edi.xml.cii",
                "html.field.history.mixin",
                "report.account.report_hash_integrity",
                "google.gmail.mixin",
                "iap.enrich.api",
                "iap.autocomplete.api",
                "image.mixin",
                "report.stock.label_lot_template_view",
                "mail.bot",
                "mail.composer.mixin",
                "mail.render.mixin",
                "mail.tracking.duration.mixin",
                "report.base.report_irmodulereference",
                "report.mrp.report_mo_overview",
                "portal.mixin",
                "report.product.report_pricelist",
                "product.catalog.mixin",
                "report.stock.label_product_product_view",
                "report.product.report_producttemplatelabel_dymo",
                "report.product.report_producttemplatelabel2x7",
                "report.product.report_producttemplatelabel4x12",
                "report.product.report_producttemplatelabel4x12noprice",
                "report.product.report_producttemplatelabel4x7",
                "stock.replenish.mixin",
                "resource.mixin",
                "account.edi.xml.ubl_sg",
                "account.edi.xml.ubl_nl",
                "spreadsheet.mixin",
                "report.stock.report_reception",
                "stock.forecasted_product_product",
                "stock.forecasted_product_template",
                "report.stock.report_stock_rule",
                "template.reset.mixin",
                "account.edi.xml.ubl_20",
                "account.edi.xml.ubl_21",
                "purchase.edi.xml.ubl_bis3",
                "account.edi.xml.ubl_bis3",
                "sale.edi.xml.ubl_bis3",
                "_unknown",
                "utm.mixin",
                "utm.source.mixin",
                "stock.warn.insufficient.qty",
            ]

            missing_models = []
            models = self.env['ir.model'].search([
                ('model', 'not like', 'ir.%'),
                ('model', 'not like', 'res.%'),
            ])
            for model in models:
                if model.model in whitelisted_models:
                    continue  # Skip known models
                access_count = self.env['ir.model.access'].search_count([
                    ('model_id', '=', model.id)
                ])
                if access_count == 0:
                    missing_models.append(model.model)

            if missing_models:
                formatted_list = "".join(f"<li>{model}</li>" for model in missing_models)
                message = f"Missing access rules for the following models:<ul>{formatted_list}</ul>"
                return False, message
            return True, "All critical models have access rules defined."
        except Exception as e:
            _logger.error("Error checking access rules: %s", e)
            return False, str(e)

    def run_scan(self):
        """Run the security scan."""
        self.ensure_one()
        self.notes = ""
        verbose_notes = ""

        checks = [
            ('master_password_set', self._check_master_password),
            ('https_enabled', self._check_https),
            ('log_file_present', self._check_log_file),
            ('db_filter_set', self._check_db_filter),
            ('db_listing_disabled', self._check_db_listing),
            ('access_rules_defined', self._check_access_rules),
        ]

        passed_count = 0
        total_checks = len(checks)

        verbose_notes += '<div style="font-family: Arial, sans-serif; font-size: 14px;">'
        verbose_notes += "<h3>🔎 Security Scan Results</h3>"
        verbose_notes += "<ul style='list-style: none; padding: 0;'>"

        for field_name, check_method in checks:
            result, msg = check_method()
            setattr(self, field_name, result)

            icon = "✅" if result else "❌"
            color = "green" if result else "red"
            if result:
                passed_count += 1

            verbose_notes += f"<li style='margin-bottom:8px;'><span style='font-weight:bold;color:{color};'>{icon} {field_name.replace('_', ' ').title()}:</span> {msg}</li>"

        verbose_notes += "</ul>"

        # Final score
        verbose_notes += f"<hr/><p style='font-size:16px;'><b>Security Score:</b> {passed_count}/{total_checks} Passed ✅</p>"
        verbose_notes += "</div>"

        self.notes = verbose_notes
        self.state = 'done'

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


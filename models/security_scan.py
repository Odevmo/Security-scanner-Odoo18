from odoo import models, fields, api
from datetime import datetime
import logging

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

    notes = fields.Text(string='Notes')
    progress = fields.Integer(string='Progress', default=0)
    running_scan = fields.Boolean(string='Running Scan', default=False)
    scan_completed = fields.Boolean(string='Scan Completed', default=False)

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
            return base_url and base_url.startswith('https://'), f"Base URL is '{base_url}'"
        except Exception as e:
            _logger.error("Error checking HTTPS: %s", e)
            return False, str(e)

    def _check_access_rules(self):
        try:
            missing_models = []
            models = self.env['ir.model'].search([
                ('model', 'not like', 'ir.%'),
                ('model', 'not like', 'res.%'),
            ])
            for model in models:
                access_count = self.env['ir.model.access'].search_count([
                    ('model_id', '=', model.id)
                ])
                if access_count == 0:
                    missing_models.append(model.model)
            if missing_models:
                return False, f"Missing access rules for: {', '.join(missing_models)}"
            return True, "All models have access rules defined."
        except Exception as e:
            _logger.error("Error checking access rules: %s", e)
            return False, str(e)

    def _check_log_file(self):
        try:
            log_level = self.env['ir.config_parameter'].sudo().get_param('logging_level')
            return bool(log_level), f"Log level is set to '{log_level}'" if log_level else "Log level not set."
        except Exception as e:
            _logger.error("Error checking log file: %s", e)
            return False, str(e)

    def _check_db_filter(self):
        try:
            dbfilter = self.env['ir.config_parameter'].sudo().get_param('database_filter')
            return bool(dbfilter), f"Database filter: '{dbfilter}'" if dbfilter else "No database filter set."
        except Exception as e:
            _logger.error("Error checking DB filter: %s", e)
            return False, str(e)

    def _check_db_listing(self):
        try:
            db_list = self.env['ir.config_parameter'].sudo().get_param('database_list')
            return db_list == 'False', f"Database listing: {db_list}"
        except Exception as e:
            _logger.error("Error checking DB listing: %s", e)
            return False, str(e)

    def run_scan(self):
        self.running_scan = True
        self.scan_completed = False
        self.progress = 0
        self.notes = ""
        verbose_notes = ""

        checks = [
            ('master_password_set', self._check_master_password),
            ('https_enabled', self._check_https),
            ('access_rules_defined', self._check_access_rules),
            ('log_file_present', self._check_log_file),
            ('db_filter_set', self._check_db_filter),
            ('db_listing_disabled', self._check_db_listing),
        ]

        total_checks = len(checks)
        for idx, (field_name, check_method) in enumerate(checks):
            result, msg = check_method()
            setattr(self, field_name, result)
            verbose_notes += f"{field_name.replace('_', ' ').title()}: {msg}\n"
            self.progress = (idx + 1) * (100 // total_checks)

        self.progress = 100
        self.running_scan = False
        self.scan_completed = True
        self.notes = verbose_notes.strip()

        return True

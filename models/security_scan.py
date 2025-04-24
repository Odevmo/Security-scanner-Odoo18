from odoo import models, fields, api
from odoo.exceptions import UserError
import subprocess
import socket
import logging

_logger = logging.getLogger(__name__)

class SecurityScan(models.Model):
    _name = 'security.scan'
    _description = 'Security Scan'

    name = fields.Char(string='Scan Name', required=True)
    scan_date = fields.Datetime(string='Scan Date', default=fields.Datetime.now)
    master_password_set = fields.Boolean(string='Master Password Set')
    https_enabled = fields.Boolean(string='HTTPS Enabled')
    access_rules_defined = fields.Boolean(string='Access Rules Defined')
    log_file_present = fields.Boolean(string='Log File Present')
    db_filter_set = fields.Boolean(string='DB Filter Set')
    db_listing_disabled = fields.Boolean(string='DB Listing Disabled')
    notes = fields.Text(string='Notes')
    progress = fields.Integer(string='Progress', default=0)
    running_scan = fields.Boolean(string='Running Scan', default=False)


    def _check_master_password(self):
        """Check if a master password is set."""
        #  check for a master password.
        master_password = self.env.cr.execute("SELECT count(*) FROM ir_config_parameter WHERE key='auth_master'")
        master_password_count = self.env.cr.fetchone()[0]
        return master_password_count > 0

    def _check_https(self):
        """Check if the Odoo instance is running over HTTPS."""
        #  check if the Odoo instance is running over HTTPS.
        try:
            # Get the Odoo server URL from the system parameters
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not base_url:
                return False  # Cannot determine, assume not secure.

            #  basic check, more robust checking would require checking the actual certificate.
            return base_url.startswith('https://')
        except Exception as e:
            _logger.error("Error checking HTTPS: %s", e)
            return False  # Error occurred, consider it not secure

    def _check_access_rules(self):
        """Check if access rules are defined for all models."""
        #  check if access rules are defined for all models.
        try:
            # Get all non-abstract, non-transient models
            models = self.env['ir.model'].search([
                ('is_abstract', '=', False),
                ('is_transient', '=', False),
                ('model', 'not like', 'ir.%'),  # Exclude Odoo internal models
                ('model', 'not like', 'res.%'),
            ])
            for model in models:
                # Check if any access rules exist for the model
                access_count = self.env['ir.model.access'].search_count([
                    ('model_id', '=', model.id)
                ])
                if access_count == 0:
                    return False  # Found a model with no access rules
            return True  # All models have access rules
        except Exception as e:
            _logger.error("Error checking access rules: %s", e)
            return False

    def _check_log_file(self):
        """Check if a log file is present."""
        # check if a log file is present
        try:
            log_level = self.env['ir.config_parameter'].sudo().get_param('logging_level')
            if log_level:
                return True
            else:
                return False
        except Exception as e:
            _logger.error("Error checking log file: %s", e)
            return False

    def _check_db_filter(self):
        """Check if a database filter is set."""
        # check if a database filter is set.
        try:
            dbfilter = self.env['ir.config_parameter'].sudo().get_param('database_filter')
            return bool(dbfilter)
        except Exception as e:
            _logger.error("Error checking db filter: %s", e)
            return False

    def _check_db_listing(self):
        """Check if database listing is disabled."""
        # check if database listing is disabled.
        try:
            db_list = self.env['ir.config_parameter'].sudo().get_param('database_list')
            if db_list == 'False':
                return True
            else:
                return False
        except Exception as e:
            _logger.error("Error checking db listing: %s", e)
            return False

    def run_scan(self):
        """Run the security scan."""
        self.running_scan = True
        self.progress = 0
        # Use a new thread to run the scan so it doesn't block the UI.
        # Clear previous results
        self.master_password_set = False
        self.https_enabled = False
        self.access_rules_defined = False
        self.log_file_present = False
        self.db_filter_set = False
        self.db_listing_disabled = False
        self.notes = ""

        # Perform the checks and update the record
        self.master_password_set = self._check_master_password()
        self.progress = 16
        self.https_enabled = self._check_https()
        self.progress = 33
        self.access_rules_defined = self._check_access_rules()
        self.progress = 50
        self.log_file_present = self._check_log_file()
        self.progress = 66
        self.db_filter_set = self._check_db_filter()
        self.progress = 83
        self.db_listing_disabled = self._check_db_listing()
        self.progress = 100
        self.running_scan = False

        # Prepare the notification message
        message = "Security Scan Results:\n\n"
        message += f"Master Password Set: {self.master_password_set}\n"
        message += f"HTTPS Enabled: {self.https_enabled}\n"
        message += f"Access Rules Defined: {self.access_rules_defined}\n"
        message += f"Log File Present: {self.log_file_present}\n"
        message += f"DB Filter Set: {self.db_filter_set}\n"
        message += f"DB Listing Disabled: {self.db_listing_disabled}\n"

        # Display the results in a popup window
        return {
            'type': 'ir.actions.act_window',
            'title': 'Security Scan Results',
            'view_mode': 'form',
            'res_model': 'security.scan',
            'res_id': self.id,
            'context': {'default_notes': message},
            'target': 'new',
        }
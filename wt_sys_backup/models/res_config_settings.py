# -*- coding: utf-8 -*-

import logging
from lxml import etree
from odoo import api, fields, models, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    app_db_backup_save_path = fields.Char('DB Backup Save Path', help="Save file in ...")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        app_db_backup_save_path = ir_config.get_param('app_db_backup_save_path', default='/home/wplus14/backup')
        res.update(app_db_backup_save_path=app_db_backup_save_path)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("app_db_backup_save_path", self.app_db_backup_save_path)


# -*- coding: utf-8 -*-
import base64
import os
import requests
import logging

from datetime import datetime

from requests import HTTPError

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class RecreateBackUp(models.Model):
    _name = 'recreate_sys_backup.backup'

    name = fields.Char("Client Name")
    start_date = fields.Date("Start Date")
    domain_main = fields.Char("Domain", help="http://demo2.wpluserp.com")
    domain = fields.Char("Backup Url", help="http://demo2.wpluserp.com")
    db_name = fields.Char("DB Name")
    db_master_password = fields.Char("DB Master Password")
    description = fields.Text("Description")
    backup_line = fields.One2many(
        'recreate_sys_backup.record', 'backup_id', string='Backup Lines', auto_join=True)
    keep_days = fields.Integer("Keep Days", default=7)
    state = fields.Boolean("Active", default=False)

    def _cron_daily_backup(self):
        backup_list = self.env['recreate_sys_backup.backup'].search(
            [('state', '=', True)])
        _logger.info("********* backup_log_cron_daily_backup_start **********")
        for client in backup_list:
            try:
                client.back_up_action()
                self.env.cr.commit()
            except Exception as e:
                self.send_error_mail(client)
                self.env.cr.rollback()
        _logger.info("********* backup_log_cron_daily_backup_end **********")

    def run_manually(self):
        for item in self:
            item.back_up_action()

    # def run_manually2(self):
    #     for item in self:
    #         self.send_error_mail(item)

    def send_error_mail(self, client):
        template = self.env.ref(
            'recreate_sys_backup.mail_template_backup_error', raise_if_not_found=False)
        super_user = self.env['res.users'].browse(2)
        template_values = {
            'email_from': super_user.partner_id.email,
            'email_to': super_user.partner_id.email,
            'auto_delete': False,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)
        if template:
            template.send_mail(client.id, force_send=True)

    def back_up_action(self):
        now = datetime.now()
        datetime_format = now.strftime("%Y_%m_%d_%H_%M_%S")
        file_name = '%s_%s.zip' % (self.db_name, datetime_format)
        is_success, file_size, msg = self.back_db(
            "%s/web/database/backup" % self.domain, self.db_master_password, self.db_name, file_name)
        _logger.info("backup_log_request_end", msg)
        backup_db_line = []
        for rec in self.backup_line:
            backup_db_line.append((0, 0, {
                'name': rec.name,
                'back_date': rec.back_date,
                'db_path': rec.db_path,
                'db_size': rec.db_size,
                'is_success': rec.is_success,
                'status': rec.status
            }))
        self.backup_line = [(6, 0, [])]
        new_record = (0, 0, {
            'name': file_name,
            'back_date': now,
            'db_path': file_name,
            'db_size': "%s MB" % file_size,
            'is_success': is_success,
            'status': msg
        })
        backup_db_line.append(new_record)
        self.write({'backup_line': backup_db_line})
        if is_success and len(self.backup_line) > self.keep_days:
            ir_config = self.env['ir.config_parameter'].sudo()
            backup_files_path = ir_config.get_param('app_db_backup_save_path')
            current_backup_dbs = self.backup_line[self.keep_days:]
            for current_db in current_backup_dbs:
                db_file_path = '%s/%s' % (backup_files_path, current_db.name)
                if os.path.isfile(db_file_path):
                    os.remove(db_file_path)
                current_db.unlink()

    def back_db(self, url, password, db_name, file_name):
        form_data = {
            "master_pwd": password,
            "name": db_name,
            "backup_format": "zip"
        }
        # Create Backup Folder
        ir_config = self.env['ir.config_parameter'].sudo()
        backup_files_path = ir_config.get_param('app_db_backup_save_path')
        if not os.path.exists(backup_files_path):
            os.makedirs(backup_files_path)
        try:
            _logger.info("backup_log_response_start %s" % db_name)
            s = requests.session()
            s.keep_alive = False
            response = requests.post(url, data=form_data, stream=True,
                                     timeout=600, verify=False, headers={'Connection': 'close'})
            _logger.info("backup_log_response_end %s" % db_name)
            zip_file = open(os.path.join(backup_files_path, file_name), 'wb')
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1024):
                zip_file.write(chunk)
            file_size = round(
                os.fstat(zip_file.fileno()).st_size / 1024 / 1024, 2)
            zip_file.close()
            backup_successful = True
            is_ex = ""
        except Exception as ex:
            print("Connection timed out!")
            _logger.info("backup_log_response_error %s" % db_name, ex)
            backup_successful = False
            file_size = 0
            is_ex = ex
        return backup_successful, file_size, is_ex


class RecreateDataBaseRecord(models.Model):
    _name = 'recreate_sys_backup.record'
    _order = 'back_date desc'
    backup_id = fields.Many2one('recreate_sys_backup.backup', string='Backup Reference', required=True, ondelete='cascade',
                                index=True, copy=False, readonly=False)
    sequence = fields.Integer(string='Sequence', default=10)

    name = fields.Char("File Name")
    back_date = fields.Datetime("Backup Date")
    db_path = fields.Char("DB Path")
    db_size = fields.Char("DB Size")
    is_success = fields.Boolean("Successful")
    status = fields.Text("Status")

    def action_download_db(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/database_custom/%s/%s' % (self.id, self.name),
        }

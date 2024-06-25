# -*- coding: utf-8 -*-
import urllib.request
import PyPDF2
import io
from odoo import http
from odoo.http import content_disposition, request
from pathlib import Path


class FileDownloadController(http.Controller):

    @http.route('/database_custom/<int:backup_id>/<string:file_name>', type='http', auth='user', csrf=False, website=True)
    def download(self, backup_id=None, file_name=None, **kw):
        backup_line_id = request.env['recreate_sys_backup.record'].sudo().browse(backup_id)
        backup_files_path = request.env['ir.config_parameter'].sudo().get_param('app_db_backup_save_path')
        db_file = Path("%s/%s" % (backup_files_path, backup_line_id.name))

        if db_file.is_file():
            download_db = open("%s/%s" % (backup_files_path, backup_line_id.name), "rb").read()
            return request.make_response(download_db, headers=[('Content-Type', 'application/zip')])
        else:
            return request.render('website.page_404')

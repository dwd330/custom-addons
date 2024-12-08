from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.addons.phone_validation.tools import phone_validation
import requests
import logging
import time
import csv
from io import StringIO
from datetime import datetime, timedelta
import phonenumbers

_logger = logging.getLogger(__name__)

class TikTokLead(models.Model):
    _name = 'tiktok.lead'
    _description = 'TikTok Lead'

    lead_id = fields.Char(string='Lead ID', readonly=True, index=True)
    created_time = fields.Datetime(string='Created Time', readonly=True)
    ad_id = fields.Char(string='Ad ID', readonly=True)
    ad_name = fields.Char(string='Ad Name', readonly=True)
    adgroup_id = fields.Char(string='Ad Group ID', readonly=True)
    adgroup_name = fields.Char(string='Ad Group Name', readonly=True)
    campaign_id = fields.Char(string='Campaign ID', readonly=True)
    campaign_name = fields.Char(string='Campaign Name', readonly=True)
    form_id = fields.Char(string='Form ID', readonly=True)
    form_name = fields.Char(string='Form Name', readonly=True)
    partner_name = fields.Char(string='partner name', readonly=True)
    phone = fields.Char(string='Phone number', readonly=True)


    def _get_config_param(self, key, error_message):
        param = self.env['ir.config_parameter'].sudo().get_param(key)
        if not param:
            _logger.error("Error finding the config",error_message)
            return False

        return param

    def convert_tiktok_time(self, time_str):
        if not time_str:
            return False
        try:
            clean_time_str = time_str.replace('(UTC+00:00)', '').strip()
            # Parse the date in `YYYY-MM-DD HH:MM:SS` format
            dt = datetime.strptime(clean_time_str, '%Y-%m-%d %H:%M:%S')
            # Convert to Odoo-compatible datetime string
            return fields.Datetime.to_string(dt)
        except ValueError as e:
            _logger.error("Error converting time string: %s", e)
            return False

    def _request(self, url, method='POST', headers=None, params=None, json_data=None):
        try:
            response = requests.request(method, url, headers=headers, params=params, json=json_data)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            return (response.json() if 'application/json' in content_type else response.content)
        except requests.HTTPError as e:
            _logger.error("HTTP error: %s", e)
            raise UserError("HTTP error occurred with TikTok API.")
        except requests.RequestException as e:
            _logger.error("Request error: %s", e)
            raise UserError("Request error with TikTok API.")
        except ValueError as e:
            _logger.error("Parsing error: %s", e)
            raise UserError("Parsing error with TikTok API.")
    def get_tiktok_access_token(self):
        app_id = self._get_config_param('tiktok.app_id', "TikTok App ID not configured.")
        secret = self._get_config_param('tiktok.secret', "TikTok Secret not configured.")
        auth_code = self._get_config_param('tiktok.auth_code', "TikTok Auth Code not configured.")

        url = 'https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/'
        headers = {'Content-Type': 'application/json'}
        payload = {'app_id': app_id, 'secret': secret, 'auth_code': auth_code}

        response_data = self._request(url, headers=headers, json_data=payload)
        _logger.info("TikTok Access Token Response: %s", response_data)

        if response_data.get('code') == 0 and 'data' in response_data:
            access_token = response_data['data'].get('access_token')
            if access_token:
                self.env['ir.config_parameter'].sudo().set_param('tiktok.access_token', access_token)
                print(self._get_config_param('tiktok.access_token', "Access Token not configured."))
                _logger.info("Access token retrieved and stored successfully.")
                return access_token
            _logger.error("Access token not found in response.")
            raise UserError("Access token not found in the TikTok API response.")
        raise UserError(f"Failed to retrieve access token: {response_data.get('message', 'Unknown error.')}")

    def get_task_id(self, access_token, advertiser_id,page_id):
        url = 'https://business-api.tiktok.com/open_api/v1.3/page/lead/task/'
        params = {
            'advertiser_id': advertiser_id,
            'page_id': page_id,
        }
        headers = {'Access-Token': access_token, 'Content-Type': 'application/json'}
        #requst task_data
        task_data = self._request(url, headers=headers, json_data=params)
        _logger.info("TikTok Lead Task Response: %s", task_data)

        if task_data.get('code') == 0 and 'data' in task_data:
            task_id = task_data['data'].get('task_id')
            if task_id:
                time.sleep(10)
                return task_id
            _logger.error("Task ID not found in response.")
            raise UserError("Task ID not found in the TikTok API response.")
        raise UserError(f"Failed to start lead task: {task_data.get('message', 'Unknown error.')}")

    def download_tiktok_leads(self, task_id, access_token, advertiser_id):
        url = 'https://business-api.tiktok.com/open_api/v1.3/page/lead/task/download/'
        headers = {'Access-Token': access_token, 'Content-Type': 'application/json'}
        params = {'advertiser_id': advertiser_id, 'task_id': task_id}

        csv_content = self._request(url, method='GET', headers=headers, params=params)
        if isinstance(csv_content, bytes):  # Handle as binary content
            return csv_content.decode('utf-8')
        raise UserError("TikTok API did not return CSV content.")

    def process_tiktok_leads(self, csv_content):
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        for row in reader:
            lead_id = row.get('\ufefflead_id', '').lstrip('\ufeff')
            created_time = self.convert_tiktok_time(row.get('created_time'))
            if lead_id and not self.search([('lead_id', '=', lead_id)]):
                tiktok_lead =self.create({
                    'lead_id': lead_id,
                    'created_time': created_time,
                    'ad_id': row.get('ad_id'),
                    'ad_name': row.get('ad_name'),
                    'adgroup_id': row.get('adgroup_id'),
                    'adgroup_name': row.get('adgroup_name'),
                    'campaign_id': row.get('campaign_id'),
                    'campaign_name': row.get('campaign_name'),
                    'form_id': row.get('form_id'),
                    'form_name': row.get('form_name'),
                    'partner_name': row.get('Name') or row.get('الاسم'),
                    'phone': row.get('Phone number') or row.get('رقم الهاتف'),
                })
                self.env.cr.commit()

                if tiktok_lead.phone:
                    self.convert_to_odoo_lead(tiktok_lead)

    def _format_phone_number(self, phone, country_code=False, country_phone_code=False):
        if phone:
            if not country_code and not country_phone_code:
                country_code = 'AE'
                country_phone_code = '+971'
            formatted_phone = phone_validation.phone_format(phone, country_code, country_phone_code)
            return formatted_phone
        return phone


    def convert_to_odoo_lead(self, tiktok_lead):
        if not tiktok_lead.phone:
            raise UserError("No phone number provided for lead conversion.")

        # Validate phone number for odoo
        tiktok_lead.phone = self._format_phone_number(tiktok_lead.phone)

        # Retrieve or create the campaign associated with this lead
        campaign = self.env['utm.campaign'].sudo().search([('name', 'like', tiktok_lead.campaign_name)], limit=1)
        if not campaign:
            campaign = self.env['utm.campaign'].sudo().create({'name': tiktok_lead.campaign_name})
            _logger.info(f'Campaign created: {campaign.name}')

        # Retrieve or create a source for this lead
        source = self.env['utm.source'].sudo().search([('name', '=', 'TikTok')], limit=1)
        if not source:
            source = self.env['utm.source'].sudo().create({'name': 'TikTok'})
            _logger.info(f'Source created: {source.name}')

        # Find or create the contact (res.partner) based on phone number
        partner = self.env['res.partner'].sudo().search([('phone', '=', tiktok_lead.phone)], limit=1)
        lang = self.env['res.lang'].search([('name', 'ilike', 'English')])

        if not partner:
            new_partner = self.env['res.partner'].sudo().create({
                'name': tiktok_lead.partner_name,
                'phone': tiktok_lead.phone,
                'lang': lang.code,
                'campaign_id': campaign,
                'source_id': source
            })
            partner = new_partner

        # Retrieve the sales team and user from config
        sales_team_from_config = self._get_config_param('tiktok.sales_team_id', "sales team not configured.")
        sales_person_from_config = self._get_config_param('tiktok.salesperson_id', "sales person not configured.")

        # Validate sales team
        sales_team = self.env['crm.team'].sudo().search([('id', '=', sales_team_from_config)], limit=1)
        if not sales_team:
            raise UserError(
                f"Sales team with ID {sales_team_from_config} does not exist. Please configure a valid sales team.")

        # Validate salesperson
        sales_person = self.env['res.users'].sudo().search([('id', '=', sales_person_from_config)], limit=1)
        if not sales_person:
            raise UserError(
                f"Salesperson with ID {sales_person_from_config} does not exist. Please configure a valid salesperson.")

        # Prepare lead data
        lead_data = {
            'phone': tiktok_lead.phone,
            'user_id': sales_person.id if sales_person else False,
            'team_id': sales_team.id if sales_team else False,
            'campaign_id': campaign.id,
            'source_id': source.id,
            'partner_id': partner.id,
            'lang_id': lang.id,
        }
        # Check if a lead exists
        lead_exists = self.env['crm.lead'].sudo().search([('phone', '=', tiktok_lead.phone)], limit=1)
        if lead_exists:
            _logger.info(f'lead exists: {lead_exists}')

        lead_stage_exist = self.env['crm.lead'].sudo().search(
            [('phone', '=', tiktok_lead.phone), ('stage_id.is_won', '!=', True)], limit=1)
        if lead_exists or lead_stage_exist:
            _logger.info(f"Lead already exists. Skipping creation.")

        else:
            # create new lead
            lead = self.env['crm.lead'].sudo().create(lead_data)
            _logger.info(f'Lead created: {lead.id}')

    #main function for tikok leads
    def get_tiktok_leads(self):
        access_token = self._get_config_param('tiktok.access_token', "Access Token not configured.")
        print('access_token:', access_token)
        if not access_token:
            #self.get_tiktok_access_token()
            access_token ='94ff21224f0f1d51bea75984853482839da43b66' #test

        advertiser_id = self._get_config_param('tiktok.advertiser_id', "Advertiser ID not configured.")
        page_ids = self._get_config_param('tiktok.page_id', "Page IDs not configured.").split(',')

        for page_id in page_ids:
            page_id = page_id.strip()
            if not page_id:
                continue

            try:
                _logger.info(f"Processing leads for Page ID: {page_id}")
                task_id = self.get_task_id(access_token, advertiser_id, page_id)
                csv_content = self.download_tiktok_leads(task_id, access_token, advertiser_id)
                if csv_content:
                    self.process_tiktok_leads(csv_content)
            except UserError as e:
                _logger.error(f"Error processing Page ID {page_id}: {str(e)}")
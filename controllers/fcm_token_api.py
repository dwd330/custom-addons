# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request, Response
import json


class FcmController(http.Controller):

    @http.route('/api/fcm/token', type='json', auth='public', methods=['POST'], csrf=False)
    def create_fcm_token(self, **kwargs):
        # Extracting the name and data from the incoming JSON
        response = http.request.httprequest.data
        response_str = response.decode('utf-8')
        response_dict = json.loads(response_str)
        token = response_dict.get('token')
        user = response_dict.get('user')

        if not token:
            return {'status': 'error',
                    'message': 'Token is required'}

        # Check if the token already exists in the database
        existing_token = request.env['fcm.token'].sudo().search([('token', '=', token)], limit=1)

        if existing_token:
            # Token already exists, return a message
            return {
                'status': 'success',
                'message': 'FCM token already exists'
            }
        else:
            # Create a new FCM token record
            request.env['fcm.token'].sudo().create({
                'token': token,
                'user': user  # Store the user associated with the token
            })
            return {
                'status': 'success',
                'message': 'FCM token created',
            }

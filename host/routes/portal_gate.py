# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for
from sqlalchemy import select, exists
from utils import GateABC
from models import Tolopica


# Starting Point for each Routes: Portal
# as like as "Portal Site".

class PortalGate(GateABC):
    def register(self, bp):
        # 1. Ordinary pages.
        # index page
        bp.add_url_rule('/', view_func=self.index, endpoint='index')

        # 2. Register Error Handler to the Application Globally.
        # Using bp.app_errorhandler makes this handler able to catch errors outside of Blueprint.
        bp.app_errorhandler(404)(self.not_found_error)
        bp.app_errorhandler(500)(self.internal_error)

    def index(self):
        """indexページ"""
        return render_template('index.html')


    def not_found_error(self, e):
        """404 error handler (Not Found)"""
        ctx = {
            'tml_title' : "404 Not Found",
            'tml_message' : f"The requested path '{request.path}' was not found on this server."
        }
        return render_template('message.html', **ctx)


    def internal_error(self, e):
        """500 error handler（unexpected error)"""
        return render_template(
            'message.html',
            tml_title="500 Internal Server Error",
            tml_message="An unexpected error occurred within the Polaris-NA-33 system."
        ), 500


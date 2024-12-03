# TikTok Leads Odoo Module

## Config
- auth:
- ad_id:
- page_id:
- app_id:
- api_secert:

if page_id is more than one elemnet you can seperate by ','




## Overview
This module enables the management of leads sourced from TikTok, allowing for seamless integration and lead management within Odoo. Key features include lead storage, custom views, and API-based settings.

---

## Table of Contents
- [Manifest](#manifest)
- [Security](#security)
- [Models](#models)
  - [tiktok_lead.py](#tiktok_leadpy)
  - [res_config_settings.py](#res_config_settingspy)
- [Views](#views)
  - [tiktok_lead_views.xml](#tiktok_lead_viewsxml)
  - [menu.xml](#menuxml)
  - [res_config_settings_views.xml](#res_config_settings_viewsxml)
- [Usage Flow](#usage-flow)

---

## Manifest
The `__manifest__.py` file includes metadata such as module name, version, dependencies, and files to load.

---

## Security

### `ir.model.access.csv`
Defines model-specific access control, ensuring secure access for authorized users.

### `security.xml`
Additional security rules for granular control over data access.

---

## Models

### `models/tiktok_lead.py`
Main model representing TikTok leads:
- **Fields**: Stores lead details like `lead_id`, `created_time`, `ad_id`, and contact info.
- **Logic**: Business logic for validation, updates, and integration.

### `models/res_config_settings.py`
Configuration model for managing TikTok API settings:
- **Fields**: Stores API keys and feature toggles for customization.
- **User Access**: Accessible via the Odoo configuration interface.

---

## Views

### `views/tiktok_lead_views.xml`
Defines views for displaying and managing leads:
- **List View**: Overview of all leads.
- **Form View**: Detailed view for each lead, including ad and campaign details.

### `views/menu.xml`
Menu configuration to add the "TikTok Leads" section to Odoo’s navigation.

### `views/res_config_settings_views.xml`
Settings interface for managing TikTok integration and module settings.

---

## Usage Flow
1. **Access Leads**: Open the TikTok Leads menu to view or manage leads.
2. **Edit Lead Details**: Use the form view to update specific lead data.
3. **Configuration**: Manage API keys and feature toggles in the settings.

---

## Installation
1. Place the module in your Odoo `addons` directory.
2. Update Odoo module list and install the module from the Odoo backend.



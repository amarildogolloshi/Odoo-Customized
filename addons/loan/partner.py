# -*- coding: utf-8 -*-
from datetime import date
from time import strptime
from openerp import models, fields, api
import base64


class res_partner(models.Model):
    _inherit = 'res.partner'
    client_no = fields.Char(string='Client No', size=15)
    old_client_no = fields.Char(string='Old Client Number', size=8)
    citizenship_id = fields.Many2one(comodel_name='res.country', string='Citizenship')
    lastname = fields.Char(string='Lastname', size=128)
    firstname = fields.Char(string='Firstname', size=128)
    middlename = fields.Char(string='Middle Name', size=128)
    name_suffix = fields.Char(string='Suffix', size=128)
    contact_number = fields.Char(string='Landline Number', size=30)
    complete_address = fields.Char(compute='_get_address', string='Address')
    photo = fields.Binary(string='Photo')
    birthdate = fields.Date(string='Birth Date')
    birthplace = fields.Char(string='Birth Place', size=128)
    age = fields.Integer(string='Age', store=True, compute='_compute_age')

    gender = fields.Selection([
        ('M', 'Male',),
        ('F', 'Female',),

    ], 'Gender')

    blacklisted = fields.Boolean(string='Black Listed')
    height = fields.Char(string='Height', size=64)
    weight = fields.Char(string='Weight', size=64)
    # marital_status_id = fields.Many2one(comodel_name='hr.employee.marital.status', string='Marital Status')
    marital = fields.Selection(selection=[
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status')
    mothers_maiden_name = fields.Char(string='Mothers Maiden Name', size=128)
    ctc_number = fields.Char(string='CTC Number', size=15)
    ctc_date = fields.Date(string='CTC Date')
    ctc_place_issued = fields.Char(string='CTC Place Issued', size=50)
    is_company = fields.Boolean(string='Company')
    mobile_number = fields.Char(string='Cellular Phone Number', size=20)
    tel_home = fields.Char(string='Home Telephone No', size=20)
    tel_office = fields.Char(string='Office Telephone No', size=20)
    religion_id = fields.Many2one(comodel_name='config.religion', string='Religion', required=False)
    street1 = fields.Char(string='Street 1', size=128)
    street2 = fields.Char(string='Street 2', size=128)
    district = fields.Char(string='District', size=10)
    province_id = fields.Many2one(comodel_name='config.province', related='barangay_id.city_id.province_id', string='Province')
    city_id = fields.Many2one(comodel_name='config.city', related='barangay_id.city_id', string='City/Municipality')
    barangay_id = fields.Many2one(comodel_name='config.barangay', string='Barangay', required=False)
    previous_address = fields.Char(string='Previous Address', size=150)
    tribe_id = fields.Many2one(comodel_name='config.tribe', string='Tribe')
    spouse_id = fields.Many2one(comodel_name='res.partner', string='Spouse', required=False)
    zip_code = fields.Char(string='Zip Code', size=4)
    email = fields.Char(string='E-mail', size=50)
    client_business_id =  fields.Integer('Client Business')

    # spouse information
    spouse_contact_no = fields.Char(related='spouse_id.contact_number', string='Landline Number')
    spouse_date_of_birth = fields.Date(related='spouse_id.birthdate', string='Birth Date')
    spouse_place_of_birth = fields.Char(related='spouse_id.birthplace', string='Birth Place')
    spouse_religion = fields.Many2one(comodel_name='config.religion', related='spouse_id.religion_id', string='Religion')
    spouse_citizenship = fields.Many2one(comodel_name='res.country', related='spouse_id.citizenship_id', string='Citizenship')
    spouse_mobile_no = fields.Char(related='spouse_id.mobile_number', string='Mobile Number')
    spouse_gender = fields.Selection(related='spouse_id.gender', selection=[('M','Male'),('F','Female'),], string='Gender')
    spouse_marital_status = fields.Selection(comodel_name=
        'hr.employee.marital.status', related='spouse_id.marital', string='Marital Status')
    spouse_tribe_id = fields.Many2one(comodel_name='config.tribe', related='spouse_id.tribe_id', string='Tribe')
    spouse_educational_attainment = fields.Many2one(comodel_name=
        'config.education', related='spouse_id.educational_attainment', string='Educational Attainment')
    spouse_age = fields.Integer(related='spouse_id.age', string='Age')
    spouse_ctc_no = fields.Char(related='spouse_id.ctc_number', string='CTC Number')
    spouse_ctc_date = fields.Date(related='spouse_id.ctc_date', string='Date'),
    spouse_ctc_place_issued = fields.Char(related='spouse_id.ctc_place_issued', string='Place Issued')
    spouse_occupation = fields.Char(string='Job/Employment', size=64)
    spouse_employment_period = fields.Char(string='Years in Service', size=20)
    spouse_present_employer = fields.Char(string='Name and Address of Employer', size=200)
    spouse_nature_interprise = fields.Char(string='Nature of Enterprises', size=100)
    spouse_employer_number = fields.Char(string='Contact Number', size=20)
    spouse_monthly_income = fields.Float(string='Monthly Income', digits=(16, 2))
    spouse_prev_employer = fields.Char(string='Name and Address of Previous Employer', size=200)
    spouse_prev_employment_position = fields.Char(string='Position', size=200),
    spouse_prev_employment_period = fields.Char(string='Years in Service', size=20)

    # other personal info
    educational_attainment = fields.Many2one(comodel_name='config.education', string='Educational Attainment')
    school_graduated = fields.Char('School Graduated', size=64)
    year_graduated = fields.Char('Year Graduated', size=4)
    # history_ids = fields.One2many('loan.history', 'client_id', string='Loan History')
    partner_photo = fields.Binary(compute='_get_data_filesystem', inverse='_save_image_data', string='Photo')

    property_account_payable = fields.Many2one(comodel_name=
       'account.account',
       company_dependent=True,
       string="Account Payable",
       view_load=True,
       domain="[('type', '=', 'payable')]",
       help='This account will be used instead of the default one as the payable account for the current partner')

    property_account_receivable = fields.Many2one(comodel_name=
       'account.account',
       company_dependent=True,
       string='Account Receivable',
       view_load=True,
       domain="[('type', '=', 'receivable')]",
       help='This account will be used instead of the default one as the receivable account for the current partner')

    @api.depends('street1', 'street2')
    def _get_address(self):
        for r in self:
            r_street1 = ''
            r_street2 = ''
            r_brgy = ''
            r_city = ''
            r_province = ''

            if r.street1:
                r_street1 = r.street1

            if r.street2:
                r_street2 = r.street2

            # if r.barangay_id:
            #     r_brgy = r.barangay_id.name

            # if r.city_id:
            #     r_city = r.city_id.name

            # if r.province_id:
            #     r_province = r.province_id.name

            first_comma = ', '
            if (not r_street1 and not r_street2) or not r_brgy:
                first_comma = ''
            second_comma = ', '
            if not r_brgy:
                second_comma = ''
            third_comma = ', '
            if not r_city:
                third_comma = ''

            r.complete_address = r_street1 + ' ' + r_street2 + first_comma + r_brgy + second_comma + r_city + third_comma + r_province

    @api.depends('birthdate')
    def _compute_age(self):
        for r in self:
            if r.birthdate:
                d = strptime(r.birthdate, "%Y-%m-%d")
                # Compute age as a time interval
                b_date = date(d[0], d[1], d[2])

                if date.today().day - b_date.day < 0:
                    less_day = 1
                else:
                    less_day = 0

                less_month = date.today().month - b_date.month - less_day

                if less_month < 0:
                    r.age = date.today().year - b_date.year - 1
                else:
                    r.age = date.today().year - b_date.year
            else:
                r.age = 0

    @api.depends('name',)
    def _get_data_filesystem(self):
        attachment_obj = self.env['image.fs.db']
        res_name = self.name_get()
        for r in self:
            search_args = [
                ('res_model', '=', self._name),
                ('name', '=', res_name and res_name[0][1] or False),
                ('field_name', '=', r.name)
            ]
            attachment_ids = attachment_obj.search(search_args)
            if attachment_ids:
                image_path  = attachment_obj.browse(attachment_ids)[0].filename
                try:
                    file_obj = open(image_path , 'rb')
                    image_blob = base64.encodestring(file_obj.read())
                    file_obj.close()
                    r.partner_photo = image_blob
                except Exception:
                    r.partner_photo = False

    def _save_image_data(self):
        image_obj = self.env['image.fs.db']
        for r in self:
            search_args = [
                ('res_model', '=', self._name),
                ('record_id', '=', r.id),
                ('field_name', '=', r.name)
            ]
            attachment_ids = image_obj.search(search_args)
            if r.value:
                if attachment_ids:
                    image_obj.write(attachment_ids, {'image_blob': r.value})
                else:
                    image_obj.create({
                        'res_model': self._name, 'record_id': r.id,
                        'image_blob': r.value, 'field_name': r.name
                    })
            else:
                image_obj.unlink(attachment_ids)


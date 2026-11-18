from odoo import api, fields, models
from datetime import date

class FacultyInformation(models.Model):
    _name = 'faculty.information'
    _description = "Faculty Information"



    sequence = fields.Char(string="Reference",required=True, copy=False, readonly=True,default='New')
    name = fields.Char(string="Name")
    last_name=fields.Char(string="Last Name")
    designation = fields.Selection([('principle_college','Principle College'),
                                    ('hod','HOD'),
                                ('staff','Staff')])
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age",
                         compute = "_compute_age",
                          store=True)
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    photo = fields.Binary(string ="Image")
    department_id = fields.Many2one(
        'department.information',
        string="Department"
    )
    degree_ids = fields.Many2many(
        'degree.information',
        string="Degree"
    )
    graduation_institute_id = fields.Many2one(
        'graduation.institute',
        string="Graduation Institute"
    )
    total_degrees = fields.Integer(string = "Total Degree",
                                    compute = "_compute_total_degrees",
                                    store =False)
    address = fields.Char(string="Address")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    publications = fields.Text(string="Publications")


    # calculate the age 
    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                record.age = (today.year - record.date_of_birth.year- ((today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day)))
            else:
                record.age = 0

    #calculate the total number of degree

    @api.depends('degree_ids')
    def _compute_total_degrees(self):
        # print(self,"-------------")
        for record in self:
            print(record,"---------record------------")
            record.total_degrees = len(record.degree_ids)


    """ default_get to name,email"""
    @api.model 
    def default_get(self,fields):
        res = super().default_get(fields)
        res.update({'name':'mouni','email':'mouni'})
        return res
  
    """display_name is  display two field top lift side of the form view"""
    @api.depends('name','phone')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.phone:
                record.display_name = f"[{record.phone}] + {record.name}"
            else:
                record.display_name = record.name


    """creating sequence number"""
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence','New') == 'New':
                vals['sequence'] = self.env['ir.sequence'].next_by_code('faculty.info') or 'New'
        return super().create(vals_list)
       
     
 

    
    
    
    



        













    
            

    


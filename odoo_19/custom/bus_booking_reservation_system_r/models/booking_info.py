from odoo import models, fields,api
from datetime import date
from odoo.exceptions import ValidationError
class BookingReservation(models.Model):
    _name = 'booking.info'
    _description = 'passenger_name'
  
    
    name = fields.Char(string="Sequence", required=True, copy=False, readonly=True, default='New')
    passenger_name = fields.Char(string=" Name ",required=True)
    phone_number = fields.Char(string="Phone Number",required=True,size = 10)
    email = fields.Char(string="E-mail ",required=True)
    state = fields.Selection([('draft', 'Draft'), ('booked', 'Booked'), ('cancel', 'Cancel')], default='draft', required=True)
    passenger_=fields.Float(string="Adult")
    dob=fields.Date(string="Date Of Birth")
    gender=fields.Selection([('male','Male'),
                             ('female','Female')])
    passenger_type=fields.Selection([('adult','Adult'),
                                     ('child','Child')])
    today = fields.Date(string="Date", default=fields.Date.today)
    
    age=fields.Integer(compute='_compute_age',string='Age')
    adult_male_count = fields.Integer(string="No of Adult Males")
    adult_female_count = fields.Integer(string="No of Adult Femals")
    child_male_count = fields.Integer(string="No of Males")
    child_female_count = fields.Integer(string="No of Femals")
    total_passenger = fields.Integer(string="Total Passenger",compute='compute_total_passenger',store=True)
    #route details
    from_place_id =fields.Many2one('place.info',string="From Place",required=True)
    to_place_id = fields.Many2one('place.info',required=True,string="To Place")
    total_seats=fields.Integer(string = "Total Seats",related ='class_of_service_id.number_of_seats', store=True ,readonly=True)
    available_seats=fields.Integer(string="Available Seats",compute='_compute_available_seats',store=True)
    passenger_info_ids = fields.One2many('passenger.info.line','booking_id',string="Passenger Information")
    
    #travel details
    departure=fields.Datetime(string='Departure Date',required=True)
    arrival=fields.Datetime(string='Arrival Date',required=True)
    pickup_address=fields.Char(string="pickup Address",required=True)
    destination_address = fields.Char(string='Destination Address',required=True)
    class_of_service_id=fields.Many2one('service.info',string="Class of Service", required=True,domain=[('state', '=', 'available')])
    price_per_passenger=fields.Float(string="Price Per Passenger",related ='class_of_service_id.price_of_service', store=True ,readonly=True)
    total_amount=fields.Float(string ="Total Amount",compute="_compute_total_amount")                   
    # from_boarding=fields.Many2one('boarding.info',string="pickup Addres",required=True,domain="[('place_id', '=',from_place_id)]")
   
    # to_boarding=fields.Many2one('boarding.info',string='Destination Addres',required=True,domain="[('place_id', '=',from_place_id)]")
    # #cancellled booking can't be modified
    def Write(self,vals):
        if self.state=='cancel':
            raise ValidationError("Cancelled record can't be modified ")
        

    
       
    
    #boarding point 
    @api.onchange('from_place_id', 'to_place_id','pickup_address','destination_address')
    def _onchange_from_place_to_place(self):
        if self.from_place_id :
            self.pickup_address=self.from_place_id.boarding_point_ids[0].boarding_name
        if self.to_place_id :
            self.destination_address=self.to_place_id.boarding_point_ids[0].boarding_name
    # @api.onchange('from_place_id','to_place_id','from_boarding','to_boarding')
    # def _onchange_from_to_boarding(self):
    #     domain={}
    #     if self.from_place_id:
    #         domain['from_boarding'] = [('place_id', '=', self.from_place_id)]
    #     if self.from_place_id:
    #         domain['to_boarding'] = [('place_id', '=', self.to_place_id)]
    #     return {'domain':domain} 
       
        
    
    #button Action
    def action_confirm(self):
       
        
             
        if self.state == 'cancel':
            raise ValidationError('Cancelled booking cannot be confirmed directly')
            
           
        self.state = 'booked'
        self.class_of_service_id.number_of_seats -= self.total_passenger

    def action_download_pdf(self):
        return self.env.ref(
        'bus_booking_reservation_system_r.action_bus_booking_report').report_action(self)
    
    def action_cancel(self):
         self.state = 'cancel'
         if self.state =='cancel':
              self.class_of_service_id.number_of_seats += self.total_passenger
   
      
    def action_draft(self):
        self.state='draft'
                
    #phone number validation
    @api.constrains('phone_number')
    def _check_phone_number(self):
        for rec in self:
            if not rec.phone_number.isdigit():
                raise ValidationError("phone number must be contain numbers only")
            
            if len(rec.phone_number)!=10:
                raise ValidationError("phone number must be exactly 10 digit only")            
     
    #E-mail validation        
    @api.constrains('email')
    def _check_email(self):
            if self.email and '@gmail.com' not in self.email :
                raise ValidationError("Email id must contain @ .com")
            
                
    
    
    #Booked record cannot be delete warning
    def unlink(self):
        for rec in self:
            if rec.state =='booked':
                raise ValidationError("Booked record cannot be deleted")
            return super().unlink
    
 
    
    #Total_passenger
    @api.depends('adult_male_count','adult_female_count','child_male_count','child_female_count')
    def compute_total_passenger(self):
        for rec in self:
            rec.total_passenger= (rec.adult_male_count + rec.adult_female_count + rec.child_male_count + rec.child_female_count)
    
    #passenger record count must match the total passenger
    @api.constrains('passenger_info_ids','total_passenger')
    def _check_passenger_count(self):
        
        if len(self.passenger_info_ids)!= self.total_passenger:
                raise ValidationError("passenger record count must match total passenger")
               
    #from_place and to_place    
    @api.onchange('from_place_id','to_place_id')
    def _check_from_to(self):
        
            if self.from_place_id and self.to_place_id and self.from_place_id == self.to_place_id:
                raise ValidationError("From Place and To Place should not be the same.")
               
            else:
                pass
    #age
   
    #departure Date
    @api.onchange('departure','arrival')
    def _onchnage_departure(self):
        
        if self.departure and self.arrival:
            if self.arrival > self.departure:
                 return {'warning': 
                 {
                    'title': 'Warning',
                    'message': 'Departure Date/Time should not be less than the current date.'
                }
            
            }
       
    #Arrival Date
    @api.onchange('departure','arrival', 'passenger_name','email')
    def _onchnage_departure(self):
        #passenger name upper
        if self.passenger_name:
            self.passenger_name=self.passenger_name.upper()
        #email lower
        if self.email:
            self.email=self.email.lower()
            
        if self.departure and self.arrival:
            if self.departure > self.arrival:
                 return {'warning': 
                 {
                    'title': 'Warning',
                    'message': 'Departure Date/Time should not be less than the current date.'
                }
            }
    #total amount
    @api.depends('price_per_passenger','total_passenger')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount= rec.price_per_passenger * rec.total_passenger
    
    @api.depends('total_seats','total_passenger')
    def _compute_available_seats(self):
        for rec in self:
            rec.available_seats =rec.total_seats - rec.total_passenger 
   
        
    #Restrict Booking Creation Without Passenger
    @api.constrains('total_passenger','passenger_name')
    def _check_total_passenger(self):
       # count passenger limit
       
        if self.total_passenger <=0:
            raise ValidationError('Enter a Number of passenger, Must contain Atleast one passenger')
        if self.total_passenger >=50:
            raise ValidationError('Maximum allowed passengers per booking 50')
        #  passenger Char check
        if self.passenger_name and  not self.passenger_name.isalpha():
            raise ValidationError(" passenger Name must be contain characters only")
        elif self.passenger_name.isalpha:
            duplicate_name_check = self.env['booking.info'].search_count([('passenger_name','=',self.passenger_name)])
            if duplicate_name_check > 1:
                    raise ValidationError("same passenger should not be allowed twice")
                
                
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res.update({'passenger_name': 'Justin ', 'email':'jhfdjh'})
        return res
             
                           
                           
    @api.depends('passenger_name', 'phone_number')
    def _compute_display_name(self):
        for record in self:
            if record.passenger_name and record.phone_number: 
                record.display_name = f"[{record.phone_number}] $ {record.passenger_name}"
            else:
                record.display_name = record.passenger_name    
                
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('booking.info') or 'New'
        return super().create(vals_list)       
    
               
    @api.onchange('available_seats','total_passenger','total_seats')
    def check_allowed_passenger(self):
        for rec in self:
            if rec.total_seats < rec.total_passenger:
                raise ValidationError(f'Only {rec. total_seats} seats are available for booking.')
                
    @api.constrains('departure')
    def check_departure_date(self):
        for rec in self:
            if rec.departure and rec.departure < fields.Datetime.now():
                raise ValidationError("Departure date and time cannot be in the past." )

    



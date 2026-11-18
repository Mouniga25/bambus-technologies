from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
import qrcode
from io import BytesIO


class BookingForm(models.Model):
    _name = 'booking.forms'
    _description = "Booking Forms"
    _rec_name ="passenger_name"

    # Customer Details
    passenger_name = fields.Char(string="Passenger Name", required=True)
    phone_number =  fields.Char(string="Phone Number ", required=True, size= 10)
    email = fields.Char(string="E-mail", required=True, help ="Enter the Email")

    # Route Details
    from_place_id =fields.Many2one(
        'places.info',
        string="From Place"
    )
    to_place_id =fields.Many2one('places.info',string="To Place")

    # Passenger Count
    adults_male = fields.Integer(string="Number of The Male Adults")
    adults_female = fields.Integer(string="Number of the Female Adults")
    children_male = fields.Integer(string="Number of The Male Children")
    children_female = fields.Integer(string="Number of The Female Children")
    total_passengers = fields.Integer(string="Total Passengers",
                         compute = "_compute_total_passengers",
                          store=True)
    # Travel Details
    departure_date_time = fields.Datetime(string="Departure Date/Time", required=True)
    arrival_date_time = fields.Datetime(string="Arrival Date/Time", required=True)
    pickup_address = fields.Char(string="Pickup Address")
    destination_address = fields.Char(string="Destination Address")


    classof_service_id = fields.Many2one('classof.service', string="Class Of Service")
    boarding_points_id = fields.Many2one(comodel_name='places.info')
    
    # Amount Details
    price_per_passenger = fields.Integer(string ="Price Per Passenger", related = "classof_service_id.price_of_service", store = True)
    total_amount = fields.Integer(string="Total Amount",compute = "_compute_total_amount",store=True)
    number_of_seat = fields.Integer(string="Number of seat", related = "classof_service_id.number_of_seats", store=True)
    available_seats = fields.Integer(string = "Available Seats")
    booked_date =fields.Date.today()

    #Passenger Information
    passenger_information_lines = fields.One2many(comodel_name="passenger.information.line", 
                                   inverse_name = 'passenger_information_id')
    
     
    state = fields.Selection([('draft', 'Draft'), ('booked', 'Booked'), ('cancelled', 'Cancelled')], default="draft")
    qr_image = fields.Binary(string="QR Code")   

    

    """Confirmed bookings (Booked) should not be deleted"""
    def unlink(self):
        for rec in self:
            if rec.state == "booked":
                raise ValidationError("It's confirm record we can't delete")
        return super().unlink()
    

    """Passenger Count Validation"""
    @api.constrains("total_passengers","passenger_information_lines")
    def check_passenger_count(self):
            for rec in self:
                if self.total_passengers:
                    if len(self.passenger_information_lines) > self.total_passengers:
                        raise ValidationError("check the number of the passenger")
                    if len(self.passenger_information_lines) < self.total_passengers:
                        raise ValidationError("add the passenger details")
    

    """Calculate the Number of the Passengers"""
    @api.depends('adults_male','adults_female','children_male','children_female')
    def _compute_total_passengers(self):
        for rec in self:
            rec.total_passengers = (rec.adults_male + rec.adults_female + rec.children_male + rec.children_female)
    

    """Calculate the Total amount"""
    @api.depends('price_per_passenger')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.price_per_passenger * rec.total_passengers

    """from place and to place cannot be same"""
    @api.onchange("from_place_id","to_place_id")
    def onchange_place(self):
       if self.from_place_id and self.to_place_id and self. from_place_id == self.to_place_id:
           raise ValidationError("from place and to place cannot be same")
    
    """Boarding Point"""
    @api.onchange("from_place_id","to_place_id")
    def onchange_from_place_id(self):
       if self.from_place_id:
           self.pickup_address = self.from_place_id.address_lines[0].boarding_point
       if self.to_place_id:
           self.destination_address = self.to_place_id.address_lines[0].boarding_point
    

    """Passenger Name Auto Capitalization"""
    @api.model_create_multi
    def create(self,val_lists):
        for rec in val_lists:
            if rec.get('passenger_name'):
                rec['passenger_name'] = rec['passenger_name'].upper()
        return super().create(val_lists)

 
    """Passenger name should not contain numbers"""
    @api.onchange("passenger_name")
    def onchange_passenger_name(self):
        for rec in self:
            if rec.passenger_name:
                for value in rec.passenger_name:
                    if value.isdigit():
                        raise ValidationError("Passenger Name must be letter ")
    

    """Phone number must digit only"""
    @api.onchange("phone_number")
    def onchange_phone_number(self):
        for rec in self:
            print(rec,"--------------------")
            if rec.phone_number :
                for value in rec.phone_number:
                    print(value,"------------------------------")
                    if value.isalpha():
                        raise ValidationError("phone number must be digit ")
    
    """Validate email format"""
    @api.onchange("email")
    def onchange_email(self):
            if self.email:
                if '.com' not in self.email or '@' not in self.email:
                    raise ValidationError("validate error email format @gamil.com")
      
    @api.model_create_multi
    def create(self,val_list):
        for rec in val_list:
            if rec.get('email'):
                rec['email'] = rec['email'].lower()
        records = super().create(val_list)
        return records
    
    """From place and To place not a same places"""
    @api.onchange("departure_date_time","arrival_date_time")
    def onchange_to_place(self):
            if self.departure_date_time and self.arrival_date_time and self.departure_date_time >= self.arrival_date_time:
                raise ValidationError("Arrival Date/Time should always be greater than Departure Date/Time.")
    
    # """"Past travel date not allowed."""
    # @api.onchange("departure_date_time")
    # def onchange_to_place(self):
    #         if self.departure_date_time and self.departure_date_time < self.fields.Datetime.now():
    #             raise ValidationError("Past travel date not allowed.")

    @api.onchange("passenger_name")
    def onchange_passenger_name(self):
        passenger_names=[]
        for rec in self.passenger_information_lines:
            if rec.name:
                name = rec.name.strip().lower()
                if name in passenger_names:
                    raise ValidationError("passenger name should not same name ")
                passenger_names.append(name)
    
    
                            
    #########
    # Action
    #########

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_booked(self):
        self.write({'state': 'booked'})
        for rec in self:
            if rec.classof_service_id.number_of_seats < rec.total_passengers :
                raise ValidationError("number of seats less than total passengers")
            rec.available_seats = rec.classof_service_id.number_of_seats - rec.total_passengers
            rec.state = "booked"            
        
        if not self.passenger_information_lines:
            raise ValidationError("Enter the passenger details")
        
        if self.total_passengers <= 0:
            raise ValidationError("total passenger greater than 0 ")
        if not self.classof_service_id:
            raise ValidationError("select class od service")

    def action_cancelled(self):
        self.write({'state': 'cancelled'})
    
    """passenger limit validation"""
    @api.onchange("age")
    def onchange_age(self):
        if len(self.passenger_information_lines.age) > 50 :
            raise ValidationError("maximum 50 passengers are aloowed")
    
    # """...cancelled cannot be editing"""
    # def write(self,vals):
    #     for rec in self:
    #         if rec.state =='booked':
    #             if "total_passengers" in vals :
    #                 raise ValidationError("passenger count cannot be change after booking")
    #     return super().write(vals)

    # """...cancelled cannot be editing"""
    # def write(self,vals):
    #     for rec in self:
    #         if rec.state =='cancelled':
    #             raise ValidationError("cancelled booking cannot be editing")
    #     return super().write(vals)
    
    # def write(self,vals):
    #     for rec in self:
    #         if "classof_service_id" in vals or "total_passengers":
    #             rec.total_amount = rec.classof_service_id.price_of_service * rec.total_passengers
    #     return super().write(vals)


    """Passenger Count Validation"""
    @api.constrains("total_passengers","passenger_information_lines")
    def check_age(self):
            for rec in self:
                if rec.total_passengers >  0 and not rec.passenger_information_lines:
                    raise ValidationError("Passenger Count Validation")
    

    def generate_qr(self):
        for rec in self:

            data = (
                f"Booking ID: {rec.id or ''} | "
                f"Passenger: {rec.passenger_name or ''} | "
                f"From: {rec.from_place_id.place_name or ''} | "
                f"To: {rec.to_place_id.place_name or ''}"
            )

            qr = qrcode.QRCode(
                version=1,
                box_size=6,
                border=2
            )

            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")

            rec.qr_image = base64.b64encode(buffer.getvalue())
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.generate_qr()
        return records



class PassengerInformationLine(models.Model):
    _name = 'passenger.information.line'
    _description = 'Passenger Information Line'


    passenger_information_id = fields.Many2one(comodel_name='booking.forms')
   
    name = fields.Char(string="Passenger Name", )
    age = fields.Integer(string="Age")
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    passenger = fields.Selection([('adult','Adult'),
                                ('children','Children')
                                ])
    seat_preference = fields.Selection([('window','Window'),
                                ('middle','Middle'),
                                ('aisle','Aisle')
                                ])
   

    # """Age Validation"""
    # @api.onchange("age")
    # def onchange_age(self):
    #     if self.age and (self.age <= 0 or self.age >= 120):
    #         raise ValidationError("Age must be greater than 0 and less than 120")
    

   
    
    
    

    """...child  passenger age must below 12"""
    @api.onchange('passenger','age')
    def onchange_passsenger_age(self):
        if self.passenger == 'children' and self.age>=12:
            raise ValidationError("children passenger age must below 12")
        if self.passenger == 'adult' and self.age<12:
            raise ValidationError("adult passenger age must above 12")

       
    @api.constrains('age')
    def _check_age(self):
         for rec in self:
             if rec.age and (rec.age <=0 or rec.age > 120):
                raise ValidationError("Age must be greater than 0 and less than 120.")



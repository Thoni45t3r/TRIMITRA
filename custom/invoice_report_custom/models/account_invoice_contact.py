from odoo import fields, models, api, _

def Terbilang(bil):
    angka=["","Satu","Dua","Tiga","Empat","Lima","Enam","Tujuh","Delapan","Sembilan","Sepuluh","Sebelas"]
    Hasil=" "
    n = int(bil)
    if n >= 0 and n <= 11:
        Hasil = Hasil + angka[n]
    elif n < 20:
        Hasil = Terbilang(n % 10) + " Belas"
    elif n < 100:
        Hasil = Terbilang(n / 10) + " Puluh" + Terbilang(n % 10)
    elif n < 200:
        Hasil = " Seratus" + Terbilang(n - 100)
    elif n < 1000:
        Hasil = Terbilang(n / 100) + " Ratus" + Terbilang(n % 100)
    elif n < 2000:
        Hasil = " Seribu" + Terbilang(n - 1000)
    elif n < 1000000:
        Hasil = Terbilang(n / 1000) + " Ribu" + Terbilang(n % 1000)
    elif n < 1000000000:
        Hasil = Terbilang(n / 1000000) + " Juta" + Terbilang(n % 1000000)
    else:
        Hasil = Terbilang(n / 1000000000) + " Miliar" + Terbilang(n % 1000000000)
    return Hasil

def indonesian_number(val):
    if val < 100:
        return _convert_nn_id(val)
    if val < 1000:
        return _convert_nnn_id(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_id))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l == 1:
                ret = denom_id[didx]
            else:
                ret = _convert_nnn_id(l) + ' ' + denom_id[didx]
            if r > 0:
                ret = ret + ', ' + indonesian_number(r)
            return ret

def amount_to_text_id(numbers, currency):
    number = '%.2f' % numbers
    units_name = currency
    liste = str(number).split('.')
    start_word = Terbilang(abs(int(liste[0])))
    
    final_result = start_word + ' ' + units_name
    return final_result 


class ResPartner(models.Model):

    _inherit = 'account.invoice'

    contact_id = fields.Many2one(
        string='Contact / UP',
        comodel_name='res.partner',
        ondelete='restrict', 
    )

    amount_to_text = fields.Text(string='In Words', store=False, readonly=True, compute='_amount_in_words')
    
    @api.one
    @api.depends('amount_total')
    def _amount_in_words(self):
        self.amount_to_text = amount_to_text_id(self.residual, "Rupiah") #amount_total
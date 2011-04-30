from django.db import models

# Create your models here.
class Factura(CommonSucursal):
    folio_num = models.PositiveIntegerField(editable=False)
    folio_serie = models.CharField(max_length=2)
    folio_num_sicofi = models.CharField(_(u'Número de aprobación del Folio'), max_length=30, unique=True)
    folio_fecha = models.DateField(_(u'Fecha de aprovación del Folio'))
    folio_rango_desde = models.PositiveIntegerField()
    folio_rango_hasta = models.PositiveIntegerField()
    venta = models.ForeignKey(Venta)
    pagada = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s - %s - %s' % (self.venta.fecha, self.folio_num, self.venta.cliente)

class Folio(CommonSucursal):
    num_sicofi = models.CharField(_(u'Número de aprobación'), help_text=_(u'El número de aprobación del folio asignado por SICOFI.'), max_length=30)
    fecha = models.DateField(_(u'Fecha de aprovación'))
    serie = models.CharField(max_length=2)
    rango_desde = models.PositiveIntegerField()
    rango_hasta = models.PositiveIntegerField()
    inicio = models.PositiveIntegerField(_(u'iniciar en'), help_text=_(u'Sólo es necesario para empezar a facturar a partir de otro número que no corresponda al inicio de esta serie. Deja en blanco para empezar desde el inicio del rango.'), blank=True, null=True)
    folio_actual = models.PositiveIntegerField(editable=False)

    def _next_folio(self):
        if not self.folio_actual:
            return self.inicio if self.inicio else self.rango_desde
        if self.folio_actual == self.rango_hasta:
            return None # use None instead of an Exception to use with the javascript api
        return self.folio_actual + 1
    next_folio = property(_next_folio)

    def _folios_left(self):
        if not self.folio_actual:
            # no folios have been used yet
            return self.rango_hasta - self.rango_desde + 1 if not self.inicio else self.rango_hasta - self.inicio + 1 # + 1 because the starting one counts too
        return self.rango_hasta - self.folio_actual
    folios_left = property(_folios_left)

    def __unicode__(self):
        return '%s - %s %d-%d' % (self.num_sicofi, self.serie, self.rango_desde, self.rango_hasta)


class Datos(CommonSucursal):
    nombre = models.CharField(_(u'nombre'), help_text=_(u'Nombre, denominación o razón social.'), max_length=50)
    calle = models.CharField(max_length=100, help_text=_(u'Calle y número int/ext'))
    colonia = models.CharField(help_text=_(u'colonia (y municipio)'), max_length=100)
    codigo_postal = models.PositiveIntegerField()
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    rfc = models.CharField('RFC', max_length=20)
    folio = models.ForeignKey(Folio, help_text=_(u'Folio para usar en la facturación.'))
    email = models.EmailField(_('e-mail address'), blank=True, null=True)
    cbb = models.ImageField(max_length=10, upload_to=get_cbb_path, blank=True, null=True, help_text=_(u'Código de Barras Bidimensional con un mínimo de 337x337 pixels y en formato .png'))

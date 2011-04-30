# Create your views here.
@login_required
def print_factura(request, venta_code, mode):
    datos = Datos.objects.get(sucursal=sucursal)
    productos = venta.ventaitem_set.all()

    # add an invoice to this venta or get existing one
    factura = venta.factura_set.all()
    if factura:
        factura = factura[0]
    else:
        # create an invoice
        fol = datos.folio
        if fol.folios_left == 0:
            return render_to_response('sucursal/generic_message.html', {'msg': 'No se puede generar la factura porque ya no hay folios disponibles en el rango actual.'}, context_instance=RequestContext(request))
        fol.folio_actual = fol.next_folio
        fol.save()
        factura = Factura(
                folio_num = fol.folio_actual,
                folio_serie = fol.serie, 
                folio_num_sicofi = fol.num_sicofi,
                folio_fecha = fol.fecha,
                folio_rango_desde = fol.rango_desde,
                folio_rango_hasta = fol.rango_hasta,
                venta=venta).save()
    if mode != 'pdf':
        return render_to_response('sucursal/factura.html', {'venta':venta, 'item_list':productos, 'datos':datos, 'factura':factura}, context_instance=RequestContext(request))
    else:
        template = get_template('sucursal/factura.html')
        context=RequestContext(request, {'venta':venta, 'item_list':productos, 'datos':datos, 'factura':factura, 'pagesize':'letter'})
        filename = 'factura.pdf'
        return print_pdf(template, filename, context)

def print_pdf(template, filename, context):
    """ returns a pdf response """
    html = template.render(context)
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
    pisa.CreatePDF(
        src = html,
        dest = response,
        link_callback = fetch_resources,
        show_error_as_pdf = True)
    return response
            
def fetch_resources(uri, rel):
    return os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))

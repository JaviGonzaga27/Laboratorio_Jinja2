import csv
from django.http import HttpResponse
from .forms import UploadCSVForms
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from .forms import ProductoForm
from tablib import Dataset


from import_export import resources


def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'listar_productos.html', {'productos': productos})

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'detalle_producto.html', {'producto': producto})

def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            # Verificar si el nombre ya está registrado
            if Producto.objects.filter(nombre=nombre).exists():
                error = f'Este nombre: "{nombre}" ya está registrado.'
                return render(request, 'crear_producto.html', {'form': form, 'error': error})
            else:
                form.save()
                return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'crear_producto.html', {'form': form})

def actualizar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'actualizar_producto.html', {'form': form})

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        return redirect('listar_productos')
    return render(request, 'eliminar_producto.html', {'producto': producto})

def export_csv(request):
    Producto_resources = resources.modelresource_factory(model=Producto)()
    dataset = Producto_resources.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_products.csv"'
    return response
    
def import_csv(request):
    if request.method == 'POST':
        form = UploadCSVForms(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES.get('file')
            if not csv_file:
                # Manejar el caso donde no se sube ningún archivo
                form.add_error('file', 'No se ha subido ningún archivo.')
            else:
                Producto_resource = resources.modelresource_factory(model=Producto)()
                dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')
                result = Producto_resource.import_data(dataset, dry_run=True)
                if not result.has_errors():
                    Producto_resource.import_data(dataset, dry_run=False)
                return redirect('listar_productos')
    else:
        form = UploadCSVForms()
    
    return render(request, 'import_csv.html', {'form': form})
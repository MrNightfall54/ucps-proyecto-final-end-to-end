import { Component, OnInit, inject, signal } from '@angular/core';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Venta, VentaService } from '../venta-service';

@Component({
  selector: 'app-detalle-venta',
  standalone: true,
  imports: [RouterLink, MatCardModule, MatButtonModule, MatDividerModule, CurrencyPipe, DatePipe],
  templateUrl: './detalle-venta.html',
  styleUrl: './detalle-venta.css'
})

export class DetalleVenta implements OnInit {
  private route = inject(ActivatedRoute);
  private ventaService = inject(VentaService);
  ventaSeleccionada = signal<Venta | undefined>(undefined);
  cargando = signal(true);
  error = signal('');

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');

    if (!id) { 
      this.cargando.set(false); 
      this.error.set('Código de venta inválido.'); 
      return; 
    }

    this.ventaService.obtenerVentaPorId(id).subscribe({
      next: venta => { 
        this.ventaSeleccionada.set(venta); 
        this.cargando.set(false); 
      },
      
      error: respuesta => {
        this.error.set(respuesta.status === 404 ? 'No existe una venta con ese código.' : 'No se pudo cargar la venta.');
        this.cargando.set(false);
      }
    });
  }
}

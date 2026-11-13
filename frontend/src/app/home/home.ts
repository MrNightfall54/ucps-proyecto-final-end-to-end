import { Component, OnInit, inject, signal } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { Venta, VentaService } from '../venta-service';
import { TablaVentas } from '../tabla-ventas/tabla-ventas';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatPaginatorModule, FormsModule, TablaVentas],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home implements OnInit {
  private ventaService = inject(VentaService);
  ventasEnPantalla = signal<Venta[]>([]);
  textoBusqueda = '';
  pagina = signal(1);
  limite = signal(20);
  total = signal(0);
  cargando = signal(false);
  error = signal('');
  private solicitud = 0;

  ngOnInit(): void { this.cargarVentas(); }

  buscarVentas(): void {
    this.pagina.set(1);
    this.cargarVentas();
  }

  cambiarPagina(evento: PageEvent): void {
    this.pagina.set(evento.pageIndex + 1);
    this.limite.set(evento.pageSize);
    this.cargarVentas();
  }

  cargarVentas(): void {
    const solicitudActual = ++this.solicitud;
    this.cargando.set(true);
    this.error.set('');
    this.ventaService.obtenerVentas(this.pagina(), this.limite(), this.textoBusqueda)
      .pipe(finalize(() => { if (solicitudActual === this.solicitud) this.cargando.set(false); }))
      .subscribe({
        next: respuesta => {
          if (solicitudActual !== this.solicitud) return;
          this.ventasEnPantalla.set(respuesta.datos);
          this.total.set(respuesta.total);
        },
        error: () => {
          if (solicitudActual !== this.solicitud) return;
          this.error.set('No se pudieron consultar las ventas. Comprueba que FastAPI y MySQL estén disponibles.');
          this.ventasEnPantalla.set([]);
          this.total.set(0);
        }
      });
  }
}

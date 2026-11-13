import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild, inject, signal } from '@angular/core';
import { CurrencyPipe, DecimalPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { Chart, registerables } from 'chart.js';
import { forkJoin } from 'rxjs';
import { VentaService, RespuestaIngresos, RespuestaUnidades } from '../venta-service';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [MatCardModule, CurrencyPipe, DecimalPipe],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})

export class Dashboard implements AfterViewInit, OnDestroy {
  @ViewChild('graficoBarras') graficoBarras!: ElementRef<HTMLCanvasElement>;
  @ViewChild('graficoDona') graficoDona!: ElementRef<HTMLCanvasElement>;

  private ventaService = inject(VentaService);
  private barras?: Chart;
  private dona?: Chart;
  cargando = signal(true);
  error = signal('');
  totalIngresos = signal(0);
  totalIgv = signal(0);
  totalUnidades = signal(0);
  totalCategorias = signal(0);

  ngAfterViewInit(): void {
    forkJoin({
      ingresos: this.ventaService.obtenerIngresos(),
      unidades: this.ventaService.obtenerUnidades()
    }).subscribe({
      next: ({ ingresos, unidades }) => {
        this.totalIngresos.set(ingresos.datos.reduce((s, d) => s + Number(d.monto_total), 0));
        this.totalIgv.set(ingresos.datos.reduce((s, d) => s + Number(d.igv), 0));
        this.totalUnidades.set(Number(unidades.total_unidades));
        this.totalCategorias.set(ingresos.datos.length);
        this.crearGraficos(ingresos, unidades);
        this.cargando.set(false);
      },
      error: () => { this.error.set('Error al consultar los dashboards de FastAPI.'); this.cargando.set(false); }
    });
  }

  private crearGraficos(ingresos: RespuestaIngresos, unidades: RespuestaUnidades): void {
    const colores = ['#2563eb', '#0d9488', '#8b5cf6', '#f59e0b', '#e11d48', '#64748b'];
    this.barras = new Chart(this.graficoBarras.nativeElement, {
      type: 'bar',
      data: {
        labels: ingresos.datos.map(d => d.categoria),
        datasets: [
          { label: 'Monto total (S/)', data: ingresos.datos.map(d => d.monto_total), backgroundColor: '#2563eb', borderRadius: 6 },
          { label: 'IGV (S/)', data: ingresos.datos.map(d => d.igv), backgroundColor: '#f59e0b', borderRadius: 6 }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        scales: { y: { beginAtZero: true, title: { display: true, text: 'Importe (S/)' } } }
      }
    });

    this.dona = new Chart(this.graficoDona.nativeElement, {
      type: 'doughnut',
      data: {
        labels: unidades.datos.map(d => d.categoria),
        datasets: [{ data: unidades.datos.map(d => d.unidades_vendidas), backgroundColor: colores, borderWidth: 3, borderColor: '#fff' }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '65%',
        plugins: {
          legend: { position: 'bottom' }, tooltip: {
            callbacks: {
              label: ctx => {
                const total = unidades.total_unidades;
                const cantidad = Number(ctx.raw);
                const pct = total > 0 ? (cantidad / total * 100).toFixed(2) : '0.00';
                return `${ctx.label}: ${cantidad} unidades (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }

  ngOnDestroy(): void {
    this.barras?.destroy();
    this.dona?.destroy();
  }
}

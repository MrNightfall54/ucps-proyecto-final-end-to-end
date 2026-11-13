import { Component, Input } from '@angular/core';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { RouterLink } from '@angular/router';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { Venta } from '../venta-service';

@Component({
  selector: 'app-tabla-ventas',
  standalone: true,
  imports: [MatTableModule, MatButtonModule, MatChipsModule, RouterLink, CurrencyPipe, DatePipe],
  templateUrl: './tabla-ventas.html',
  styleUrl: './tabla-ventas.css'
})

export class TablaVentas {
  @Input() set lista(value: Venta[]) {
    this.dataSource.data = value ?? [];
  }
  columnas = ['id_transaccion', 'categoria', 'producto', 'cantidad', 'precio_unitario', 'fecha_venta', 'stock_actual', 'monto_total', 'igv', 'acciones'];
  dataSource = new MatTableDataSource<Venta>([]);
}

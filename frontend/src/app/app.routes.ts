import { Routes } from '@angular/router';
import { Home } from './home/home';
import { DetalleVenta } from './detalle-venta/detalle-venta';
import { Dashboard } from './dashboard/dashboard';

export const routes: Routes = [
  { path: '', component: Home, title: 'Registro de Ventas' },
  { path: 'dashboard', component: Dashboard, title: 'Dashboard de Ventas' },
  { path: 'venta/:id', component: DetalleVenta, title: 'Detalle de Venta' },
  { path: '**', redirectTo: '' }
];

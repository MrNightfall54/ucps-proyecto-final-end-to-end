import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Venta {
  id_transaccion: string;
  categoria: string;
  producto: string;
  cantidad: number;
  precio_unitario: number;
  fecha_venta: string;
  stock_actual: number;
  monto_total: number;
  igv: number;
}

export interface RespuestaVentas {
  total: number;
  pagina: number;
  limite: number;
  datos: Venta[];
}

export interface IngresoCategoria {
  categoria: string;
  monto_total: number;
  igv: number;
}

export interface RespuestaIngresos { 
  datos: IngresoCategoria[]; 
}

export interface UnidadesCategoria {
  categoria: string;
  unidades_vendidas: number;
  porcentaje: number;
}

export interface RespuestaUnidades {
  total_unidades: number;
  datos: UnidadesCategoria[];
}

@Injectable({ providedIn: 'root' })
export class VentaService {
  private http = inject(HttpClient);
  private readonly api = 'http://localhost:8000/api';

  obtenerVentas(pagina = 1, limite = 20, buscar = ''): Observable<RespuestaVentas> {
    const params = new HttpParams()
      .set('pagina', pagina)
      .set('limite', limite)
      .set('buscar', buscar.trim());
    return this.http.get<RespuestaVentas>(`${this.api}/ventas`, { params });
  }

  obtenerVentaPorId(id: string): Observable<Venta> {
    return this.http.get<Venta>(`${this.api}/ventas/${encodeURIComponent(id)}`);
  }

  obtenerIngresos(): Observable<RespuestaIngresos> {
    return this.http.get<RespuestaIngresos>(`${this.api}/dashboard/ingresos`);
  }

  obtenerUnidades(): Observable<RespuestaUnidades> {
    return this.http.get<RespuestaUnidades>(`${this.api}/dashboard/unidades`);
  }
}

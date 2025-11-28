// Configuración de la API
const API_BASE = 'https://proyectoetl-production.up.railway.app';

// Variables globales
let connectionStatus = false;

// Utilidades
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toastId = `toast-${Date.now()}`;
    
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-${type === 'success' ? 'check-circle text-success' : type === 'error' ? 'exclamation-circle text-danger' : 'info-circle text-info'} me-2"></i>
                <strong class="me-auto">${type === 'success' ? 'Éxito' : type === 'error' ? 'Error' : 'Información'}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toast = new bootstrap.Toast(document.getElementById(toastId));
    toast.show();
}

// Configuración
const API_URL = 'https://proyectoetl-production.up.railway.app/api';

// Funciones de utilidad
function addLog(message, type = 'info') {
    const logsDiv = document.getElementById('logs');
    const timestamp = new Date().toLocaleTimeString();
    const colorClass = {
        'info': 'text-info',
        'success': 'text-success',
        'warning': 'text-warning',
        'error': 'text-danger'
    }[type] || 'text-light';
    
    const typeIcon = {
        'info': '',
        'success': '',
        'warning': '',
        'error': ''
    }[type] || '';
    
    logsDiv.innerHTML += `<div class="${colorClass}">[${timestamp}] ${typeIcon} ${message}</div>`;
    logsDiv.scrollTop = logsDiv.scrollHeight;
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(amount);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('es-MX');
}

// Funciones de API
async function makeRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function checkStatus() {
    try {
        addLog('Verificando estado de conexiones...', 'info');
        const status = await makeRequest('/status');
        
        connectionStatus = status.status === 'success';
        
        // Actualizar indicador de conexión (si existe el elemento antiguo)
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            if (connectionStatus) {
                statusIndicator.innerHTML = '<i class="fas fa-circle text-success"></i> Conectado';
            } else {
                statusIndicator.innerHTML = '<i class="fas fa-circle text-danger"></i> Error de conexión';
            }
        }
        
        // Actualizar indicador superior
        const statusTop = document.getElementById('connection-status-top');
        if (statusTop) {
            if (connectionStatus) {
                statusTop.innerHTML = '<i class="fas fa-circle text-success"></i> Sistema Operativo';
                addLog('Conexiones establecidas correctamente', 'success');
            } else {
                statusTop.innerHTML = '<i class="fas fa-circle text-danger"></i> Error de conexión';
                addLog('Error en las conexiones', 'error');
            }
        }
        
        // Actualizar cards de estado
        updateStatusCards(status);
        
    } catch (error) {
        connectionStatus = false;
        const statusIndicator = document.getElementById('connection-status');
        statusIndicator.innerHTML = '<i class="fas fa-circle text-danger"></i> Sin conexión';
        addLog(` Error de conexión: ${error.message}`, 'error');
        
        // Mostrar error en cards
        document.getElementById('origen-status').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Error de conexión
            </div>
        `;
        document.getElementById('destino-status').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Error de conexión
            </div>
        `;
    }
}

function updateStatusCards(status) {
    // Card origen
    const origenCard = document.getElementById('origen-status');
    if (status.origen && status.origen.conectado) {
        origenCard.innerHTML = `
            <div class="row text-center">
                <div class="col-6">
                    <h3 class="text-primary">${status.origen.proyectos}</h3>
                    <small class="text-muted">Proyectos</small>
                </div>
                <div class="col-6">
                    <h3 class="text-success">✓</h3>
                    <small class="text-muted">Conectado</small>
                </div>
            </div>
            <div class="mt-2">
                <small class="text-muted">Host: ${status.origen.host}</small>
            </div>
        `;
    } else {
        origenCard.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                No conectado
            </div>
        `;
    }
    
    // Card destino
    const destinoCard = document.getElementById('destino-status');
    if (status.destino && status.destino.conectado) {
        destinoCard.innerHTML = `
            <div class="row text-center">
                <div class="col-6">
                    <h3 class="text-success">${status.destino.hechos_proyecto}</h3>
                    <small class="text-muted">Hechos</small>
                </div>
                <div class="col-6">
                    <h3 class="text-success">✓</h3>
                    <small class="text-muted">Conectado</small>
                </div>
            </div>
            <div class="mt-2">
                <small class="text-muted">Host: ${status.destino.host}</small>
            </div>
        `;
    } else {
        destinoCard.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                No conectado
            </div>
        `;
    }
}

async function cargarDatosOrigen() {
    try {
        addLog('Cargando datos de origen...', 'info');
        const data = await makeRequest('/datos-origen');
        
        const tbody = document.getElementById('tabla-origen');
        
        if (data.proyectos_recientes && data.proyectos_recientes.length > 0) {
            tbody.innerHTML = data.proyectos_recientes.map(proyecto => `
                <tr>
                    <td>${proyecto.id}</td>
                    <td>${proyecto.nombre}</td>
                    <td>${proyecto.cliente}</td>
                    <td>${formatDate(proyecto.fecha_inicio)}</td>
                    <td>${formatCurrency(proyecto.presupuesto)}</td>
                    <td>
                        <span class="badge ${proyecto.estado === 'Completado' ? 'bg-success' : 'bg-warning'}">
                            ${proyecto.estado}
                        </span>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        <i class="fas fa-inbox"></i>
                        No hay proyectos disponibles
                    </td>
                </tr>
            `;
        }
        
        addLog(` Datos de origen cargados: ${data.proyectos_recientes?.length || 0} proyectos`, 'success');
        
    } catch (error) {
        addLog(` Error cargando datos de origen: ${error.message}`, 'error');
        document.getElementById('tabla-origen').innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Error cargando datos
                </td>
            </tr>
        `;
    }
}

async function cargarMetricas() {
    try {
        addLog('Cargando métricas del datawarehouse...', 'info');
        
        // Cargar datos de origen y datawarehouse
        const dataOrigen = await makeRequest('/datos-origen');
        const dataDW = await makeRequest('/datos-datawarehouse');
        
        // Actualizar tarjetas de métricas
        if (dataOrigen && dataOrigen.estadisticas && dataOrigen.estadisticas.Proyecto !== undefined) {
            document.getElementById('total-proyectos-origen').textContent = dataOrigen.estadisticas.Proyecto;
        }
        
        if (dataDW && dataDW.metricas) {
            document.getElementById('total-proyectos-dw').textContent = dataDW.metricas.total_proyectos || 0;
            document.getElementById('total-tareas').textContent = dataDW.metricas.total_tareas || 0;
            document.getElementById('estado-etl').textContent = 'OK';
        }
        
        // Actualizar el contenedor de métricas si existe (para compatibilidad)
        const container = document.getElementById('metricas-container');
        if (container && dataDW.metricas) {
            const { metricas } = dataDW;
            container.innerHTML = `
                <div class="col-md-3 mb-3">
                    <div class="card text-center border-primary">
                        <div class="card-body">
                            <h2 class="text-primary">${metricas.total_proyectos}</h2>
                            <p class="card-text">Proyectos Finalizados</p>
                            <small class="text-muted">Completados o Cancelados</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card text-center border-success">
                        <div class="card-body">
                            <h2 class="text-success">${formatCurrency(metricas.presupuesto_promedio)}</h2>
                            <p class="card-text">Presupuesto Promedio</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card text-center border-warning">
                        <div class="card-body">
                            <h2 class="text-warning">${Math.round(metricas.dias_promedio || 0)}</h2>
                            <p class="card-text">Días Promedio</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card text-center border-info">
                        <div class="card-body">
                            <h2 class="text-info">${metricas.proyectos_a_tiempo}</h2>
                            <p class="card-text">Proyectos a Tiempo</p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Cargar tabla de proyectos del datawarehouse
        const tbody = document.getElementById('tabla-datawarehouse');
        if (tbody) {
            if (dataDW && dataDW.proyectos && dataDW.proyectos.length > 0) {
                tbody.innerHTML = dataDW.proyectos.map(p => {
                    // Determinar badge de estado según el estado real del proyecto
                    let estadoBadge = '<span class="badge bg-secondary">Desconocido</span>';
                    if (p.estado) {
                        if (p.estado === 'Completado') {
                            estadoBadge = '<span class="badge bg-success">Completado</span>';
                        } else if (p.estado === 'Cancelado') {
                            estadoBadge = '<span class="badge bg-warning">Cancelado</span>';
                        } else if (p.estado === 'En Progreso') {
                            estadoBadge = '<span class="badge bg-primary">En Progreso</span>';
                        } else if (p.estado === 'Pendiente') {
                            estadoBadge = '<span class="badge bg-info">Pendiente</span>';
                        }
                    }
                    
                    const cumplimientoTiempo = p.cumplimiento_tiempo === 'Sí' || p.cumplimiento_tiempo === 1 ? 
                        '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                        '<span class="badge bg-danger"><i class="fas fa-times"></i></span>';
                    
                    const cumplimientoPresupuesto = p.cumplimiento_presupuesto === 'Sí' || p.cumplimiento_presupuesto === 1 ? 
                        '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                        '<span class="badge bg-danger"><i class="fas fa-times"></i></span>';
                    
                    return `
                        <tr>
                            <td>${p.id_proyecto}</td>
                            <td><strong>${p.nombre_proyecto || 'Sin nombre'}</strong></td>
                            <td>${estadoBadge}</td>
                            <td>${cumplimientoTiempo}</td>
                            <td>${p.duracion_planificada || 0} días</td>
                            <td>${p.duracion_real || 0} días</td>
                            <td>${cumplimientoPresupuesto}</td>
                            <td>${formatCurrency(p.presupuesto)}</td>
                            <td>${formatCurrency(p.costo_real)}</td>
                        </tr>
                    `;
                }).join('');
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center text-muted">
                            <i class="fas fa-inbox"></i>
                            No hay proyectos en el datawarehouse
                        </td>
                    </tr>
                `;
            }
        }
        
        addLog(` Métricas cargadas: ${dataDW?.proyectos?.length || 0} proyectos en DW`, 'success');
        
    } catch (error) {
        addLog(` Error cargando métricas: ${error.message}`, 'error');
        const container = document.getElementById('metricas-container');
        if (container) {
            container.innerHTML = `
                <div class="col-12 text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x"></i>
                    <p>Error cargando métricas</p>
                </div>
            `;
        }
    }
}

// Funciones de control
async function generarDatosPersonalizados() {
    if (!connectionStatus) {
        showToast('No hay conexión con el servidor', 'error');
        return;
    }
    
    try {
        // Obtener valores del formulario
        const clientes = parseInt(document.getElementById('num-clientes').value);
        const empleados = parseInt(document.getElementById('num-empleados').value);
        const equipos = parseInt(document.getElementById('num-equipos').value);
        const proyectos = parseInt(document.getElementById('num-proyectos').value);
        
        // Validar valores
        if (clientes < 1 || empleados < 1 || equipos < 1 || proyectos < 1) {
            showToast('Todos los valores deben ser mayores a 0', 'error');
            return;
        }
        
        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('generarDatosModal'));
        modal.hide();
        
        addLog(` Generando datos: ${clientes} clientes, ${empleados} empleados, ${equipos} equipos, ${proyectos} proyectos...`, 'info');
        showToast('Generando datos personalizados...', 'info');
        
        const result = await makeRequest('/generar-datos', {
            method: 'POST',
            body: JSON.stringify({
                clientes: clientes,
                empleados: empleados,
                equipos: equipos,
                proyectos: proyectos
            })
        });
        
        if (result.success) {
            const stats = result.stats;
            addLog(` Datos generados: ${stats.clientes} clientes, ${stats.empleados} empleados, ${stats.equipos} equipos, ${stats.proyectos} proyectos, ${stats.tareas} tareas`, 'success');
            showToast('¡Datos generados exitosamente!', 'success');
            
            // Recargar datos
            await cargarTodasTablasOrigen();
            await checkStatus();
        } else {
            throw new Error(result.message || result.error || 'Error desconocido');
        }
        
    } catch (error) {
        addLog(` Error generando datos: ${error.message}`, 'error');
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function insertarDatos() {
    if (!connectionStatus) {
        showToast('No hay conexión con el servidor', 'error');
        return;
    }
    
    try {
        addLog('Insertando datos de prueba...', 'info');
        showToast('Generando datos de prueba...', 'info');
        
        const result = await makeRequest('/insertar-datos', {
            method: 'POST'
        });
        
        addLog(' Datos insertados correctamente', 'success');
        showToast(result.message, 'success');
        
        // Recargar datos
        await checkStatus();
        
    } catch (error) {
        addLog(` Error insertando datos: ${error.message}`, 'error');
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function ejecutarETL() {
    if (!connectionStatus) {
        showToast('No hay conexión con el servidor', 'error');
        return;
    }
    
    const btnETL = document.getElementById('btn-etl');
    const originalText = btnETL.innerHTML;
    
    try {
        // Cambiar botón a estado de carga
        btnETL.disabled = true;
        btnETL.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Ejecutando ETL...';
        
        addLog(' Iniciando proceso ETL...', 'info');
        showToast('Ejecutando proceso ETL...', 'info');
        
        const result = await makeRequest('/ejecutar-etl', {
            method: 'POST'
        });
        
        addLog(' Proceso ETL completado exitosamente', 'success');
        addLog(` Registros procesados: ${JSON.stringify(result.registros_procesados)}`, 'info');
        showToast(result.message, 'success');
        
        // Recargar datos
        await cargarMetricas();
        await checkStatus();
        
    } catch (error) {
        addLog(` Error en proceso ETL: ${error.message}`, 'error');
        showToast(`Error en ETL: ${error.message}`, 'error');
    } finally {
        // Restaurar botón
        btnETL.disabled = false;
        btnETL.innerHTML = originalText;
    }
}

async function limpiarDatos() {
    if (!connectionStatus) {
        showToast('No hay conexión con el servidor', 'error');
        return;
    }
    
    if (!confirm('¿Estás seguro de que quieres eliminar todos los datos? Esta acción no se puede deshacer.')) {
        return;
    }
    
    try {
        addLog('🗑️ Limpiando todas las tablas...', 'warning');
        showToast('Eliminando todos los datos...', 'warning');
        
        const result = await makeRequest('/limpiar-datos', {
            method: 'DELETE'
        });
        
        addLog(' Datos eliminados correctamente', 'success');
        showToast(result.message, 'success');
        
        // Recargar datos
        await cargarMetricas();
        await checkStatus();
        
    } catch (error) {
        addLog(` Error limpiando datos: ${error.message}`, 'error');
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Función para cambiar de sección
function showSection(section) {
    // Remover clase active de todos los items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Agregar clase active al item clickeado
    event.target.closest('.menu-item').classList.add('active');
    
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.style.display = 'none';
    });
    
    // Mostrar la sección seleccionada
    document.getElementById(`section-${section}`).style.display = 'block';
    
    // Actualizar título
    const titulos = {
        'dashboard': 'Dashboard Principal',
        'datos-origen': 'Base de Datos Origen',
        'control-etl': 'Control ETL',
        'datawarehouse': 'DataWarehouse',
        'analisis': 'Análisis',
        'trazabilidad': 'Búsqueda y Trazabilidad'
    };
    document.getElementById('section-title').textContent = titulos[section] || 'Dashboard';
    
    // Cargar datos según la sección
    if (section === 'datos-origen') {
        cargarTodasTablasOrigen();
    } else if (section === 'datawarehouse') {
        cargarTablaDatawarehouseCompleta();
    } else if (section === 'analisis') {
        cargarAnalisis();
    } else if (section === 'trazabilidad') {
        // Limpiar formulario y resultados
        document.getElementById('form-busqueda').reset();
        document.getElementById('resultado-trazabilidad').style.display = 'none';
    }
}

// Nueva función para cargar todas las tablas del origen
async function cargarTodasTablasOrigen() {
    const container = document.getElementById('todas-tablas-origen-container');
    
    try {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Cargando todas las tablas...
            </div>
        `;
        
        const response = await makeRequest('/datos-origen/todas-tablas');
        
        if (!response.success) {
            throw new Error(response.message);
        }
        
        let html = '';
        
        response.tablas.forEach((tabla, index) => {
            const colorClasses = [
                'border-primary',
                'border-success', 
                'border-info',
                'border-warning',
                'border-danger',
                'border-secondary',
                'border-dark'
            ];
            
            const borderClass = colorClasses[index % colorClasses.length];
            
            html += `
                <div class="mb-4">
                    <div class="card ${borderClass}" style="border-width: 2px;">
                        <div class="card-header bg-light">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="fas fa-table me-2"></i>
                                    ${tabla.tabla}
                                </h5>
                                <span class="badge bg-primary">
                                    ${tabla.total_registros} registro${tabla.total_registros !== 1 ? 's' : ''}
                                </span>
                            </div>
                        </div>
                        <div class="card-body p-0">
                            ${tabla.datos.length > 0 ? `
                                <div class="table-responsive">
                                    <table class="table table-sm table-hover mb-0">
                                        <thead class="table-light">
                                            <tr>
                                                ${tabla.columnas.map(col => `<th class="text-nowrap">${col}</th>`).join('')}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${tabla.datos.map(fila => `
                                                <tr>
                                                    ${tabla.columnas.map(col => {
                                                        let valor = fila[col];
                                                        
                                                        // Formatear valores según tipo
                                                        if (valor === null || valor === undefined) {
                                                            return '<td class="text-muted">&ndash;</td>';
                                                        } else if (typeof valor === 'number' && !Number.isInteger(valor)) {
                                                            return `<td class="text-end">${valor.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>`;
                                                        } else if (typeof valor === 'number') {
                                                            return `<td class="text-end">${valor.toLocaleString('es-MX')}</td>`;
                                                        } else if (col.toLowerCase().includes('fecha')) {
                                                            return `<td class="text-nowrap">${valor}</td>`;
                                                        } else if (col.toLowerCase().includes('estado') || col.toLowerCase() === 'nombre_estado') {
                                                            let badgeClass = 'secondary';
                                                            if (valor.toLowerCase().includes('completado') || valor.toLowerCase().includes('activo')) badgeClass = 'success';
                                                            if (valor.toLowerCase().includes('cancelado')) badgeClass = 'danger';
                                                            if (valor.toLowerCase().includes('proceso') || valor.toLowerCase().includes('planificación')) badgeClass = 'warning';
                                                            if (valor.toLowerCase().includes('pausado')) badgeClass = 'secondary';
                                                            return `<td><span class="badge bg-${badgeClass}">${valor}</span></td>`;
                                                        } else {
                                                            return `<td>${valor}</td>`;
                                                        }
                                                    }).join('')}
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                                ${tabla.registros_mostrados < tabla.total_registros ? `
                                    <div class="card-footer bg-light text-muted small">
                                        <i class="fas fa-info-circle me-1"></i>
                                        Mostrando los últimos ${tabla.registros_mostrados} de ${tabla.total_registros} registros
                                    </div>
                                ` : ''}
                            ` : `
                                <div class="p-3 text-center text-muted">
                                    <i class="fas fa-inbox me-2"></i>
                                    No hay datos en esta tabla
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html || '<div class="alert alert-info">No se encontraron tablas</div>';
        
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error cargando datos: ${error.message}
            </div>
        `;
    }
}

// Funciones para cargar tablas completas
async function cargarTablaOrigenCompleta() {
    try {
        const data = await makeRequest('/datos-origen');
        const tbody = document.getElementById('tabla-origen-completa');
        
        if (data.proyectos_recientes && data.proyectos_recientes.length > 0) {
            tbody.innerHTML = data.proyectos_recientes.map(proyecto => `
                <tr>
                    <td>${proyecto.id}</td>
                    <td>${proyecto.nombre}</td>
                    <td>${proyecto.cliente}</td>
                    <td>${formatDate(proyecto.fecha_inicio)}</td>
                    <td>${formatCurrency(proyecto.presupuesto)}</td>
                    <td>
                        <span class="badge ${proyecto.estado === 'Completado' ? 'bg-success' : proyecto.estado === 'Cancelado' ? 'bg-warning' : 'bg-info'}">
                            ${proyecto.estado}
                        </span>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay datos disponibles</td></tr>';
        }
    } catch (error) {
        addLog(` Error cargando tabla origen: ${error.message}`, 'error');
    }
}

// Función de búsqueda de trazabilidad
async function buscarTrazabilidad(event) {
    event.preventDefault();
    
    const tipo = document.getElementById('busqueda-tipo').value;
    const criterio = document.getElementById('busqueda-criterio').value;
    const valor = document.getElementById('busqueda-valor').value;
    
    if (!tipo || !criterio || !valor) {
        showToast('Por favor completa todos los campos', 'error');
        return;
    }
    
    try {
        addLog(` Buscando ${tipo} por ${criterio}: ${valor}...`, 'info');
        showToast('Buscando...', 'info');
        
        const resultado = await makeRequest('/buscar-trazabilidad', {
            method: 'POST',
            body: JSON.stringify({
                tipo: tipo,
                criterio: criterio,
                valor: valor
            })
        });
        
        // Mostrar resultados
        document.getElementById('resultado-trazabilidad').style.display = 'block';
        
        // Actualizar mensaje de alerta
        const alertaDiv = document.getElementById('alerta-resultado');
        let alertClass = 'alert-info';
        let icon = '<i class="fas fa-info-circle me-2"></i>';
        
        if (resultado.encontrado_origen && resultado.encontrado_dw) {
            alertClass = 'alert-success';
            icon = '<i class="fas fa-check-circle me-2"></i>';
        } else if (resultado.encontrado_origen && !resultado.encontrado_dw) {
            alertClass = 'alert-warning';
            icon = '<i class="fas fa-exclamation-triangle me-2"></i>';
        } else {
            alertClass = 'alert-danger';
            icon = '<i class="fas fa-times-circle me-2"></i>';
        }
        
        alertaDiv.className = `alert ${alertClass} alert-dismissible fade show`;
        alertaDiv.innerHTML = `
            ${icon}
            <strong>${resultado.mensaje}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Renderizar datos de BD Origen
        const datosOrigenDiv = document.getElementById('datos-origen-resultado');
        if (resultado.encontrado_origen && resultado.datos_origen) {
            datosOrigenDiv.innerHTML = `
                <div class="badge bg-success mb-3 fs-6">
                    <i class="fas fa-check-circle me-1"></i>
                    ENCONTRADO
                </div>
                ${renderizarDatos(resultado.datos_origen, tipo)}
            `;
        } else {
            datosOrigenDiv.innerHTML = `
                <div class="badge bg-danger mb-3 fs-6">
                    <i class="fas fa-times-circle me-1"></i>
                    NO ENCONTRADO
                </div>
                <p class="text-muted">No se encontró el registro en la base de datos origen.</p>
            `;
        }
        
        // Renderizar datos de DW
        const datosDWDiv = document.getElementById('datos-dw-resultado');
        if (resultado.encontrado_dw && resultado.datos_dw) {
            datosDWDiv.innerHTML = `
                <div class="badge bg-success mb-3 fs-6">
                    <i class="fas fa-check-circle me-1"></i>
                    ENCONTRADO
                </div>
                ${renderizarDatos(resultado.datos_dw, tipo, true)}
            `;
        } else {
            datosDWDiv.innerHTML = `
                <div class="badge bg-secondary mb-3 fs-6">
                    <i class="fas fa-minus-circle me-1"></i>
                    NO ENCONTRADO
                </div>
                <p class="text-muted">
                    ${resultado.encontrado_origen ? 
                        'El registro no está en el DataWarehouse. Esto es normal si el registro no está completado/cancelado o si no se ha ejecutado el ETL.' : 
                        'No se puede buscar en el DataWarehouse si no existe en origen.'}
                </p>
            `;
        }
        
        addLog(` Búsqueda completada`, 'success');
        
        // Scroll hacia los resultados
        document.getElementById('resultado-trazabilidad').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        addLog(` Error en búsqueda: ${error.message}`, 'error');
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Función auxiliar para renderizar datos en tabla HTML
function renderizarDatos(datos, tipo, esDW = false) {
    let html = '<div class="table-responsive"><table class="table table-sm table-bordered">';
    
    // Campos específicos por tipo
    let camposRelevantes = [];
    
    if (tipo === 'proyecto') {
        if (esDW) {
            camposRelevantes = ['id_proyecto', 'nombre_proyecto', 'presupuesto', 'costo_real', 'duracion_planificada', 
                              'duracion_real', 'cumplimiento_tiempo', 'cumplimiento_presupuesto', 'tareas_total', 
                              'tareas_completadas', 'porcentaje_completado'];
        } else {
            camposRelevantes = ['id_proyecto', 'nombre', 'nombre_cliente', 'nombre_gerente', 'nombre_estado', 
                              'fecha_inicio', 'fecha_fin_plan', 'fecha_fin_real', 'presupuesto', 'costo_real', 'prioridad'];
        }
    } else if (tipo === 'cliente') {
        camposRelevantes = ['id_cliente', 'nombre', 'sector', 'contacto', 'telefono', 'email', 
                           'direccion', 'fecha_registro', 'activo'];
    } else if (tipo === 'empleado') {
        camposRelevantes = ['id_empleado', 'nombre', 'puesto', 'departamento', 'salario_base', 
                           'fecha_ingreso', 'activo'];
    } else if (tipo === 'tarea') {
        if (esDW) {
            camposRelevantes = ['id_tarea', 'id_proyecto', 'id_empleado', 'duracion_planificada', 'duracion_real', 
                              'horas_plan', 'horas_reales', 'costo_estimado', 'costo_real_tarea', 'progreso_porcentaje'];
        } else {
            camposRelevantes = ['id_tarea', 'nombre_tarea', 'nombre_proyecto', 'nombre_empleado', 'nombre_estado',
                              'fecha_inicio_plan', 'fecha_fin_plan', 'fecha_fin_real', 'horas_plan', 'horas_reales', 
                              'costo_estimado', 'costo_real', 'progreso_porcentaje'];
        }
    }
    
    // Si no hay campos relevantes definidos, mostrar todos
    if (camposRelevantes.length === 0) {
        camposRelevantes = Object.keys(datos);
    }
    
    // Renderizar cada campo
    for (let campo of camposRelevantes) {
        if (datos.hasOwnProperty(campo)) {
            let valor = datos[campo];
            let valorFormateado = valor;
            
            // Formatear según tipo de dato
            if (valor === null || valor === undefined) {
                valorFormateado = '<span class="text-muted">&ndash;</span>';
            } else if (campo.toLowerCase().includes('presupuesto') || campo.toLowerCase().includes('costo') || campo.toLowerCase().includes('salario')) {
                valorFormateado = formatCurrency(parseFloat(valor));
            } else if (campo.toLowerCase().includes('fecha') || campo.toLowerCase().includes('timestamp')) {
                valorFormateado = formatDate(valor);
            } else if (campo.toLowerCase().includes('cumplimiento')) {
                valorFormateado = valor === 1 || valor === '1' ? 
                    '<span class="badge bg-success"><i class="fas fa-check"></i> Sí</span>' : 
                    '<span class="badge bg-danger"><i class="fas fa-times"></i> No</span>';
            } else if (campo.toLowerCase() === 'activo') {
                valorFormateado = valor === 1 || valor === '1' ? 
                    '<span class="badge bg-success">Activo</span>' : 
                    '<span class="badge bg-secondary">Inactivo</span>';
            } else if (typeof valor === 'number') {
                valorFormateado = valor.toLocaleString('es-MX');
            }
            
            // Convertir snake_case a Title Case
            let nombreCampo = campo.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            html += `
                <tr>
                    <td class="fw-bold bg-light" style="width: 35%;">${nombreCampo}</td>
                    <td>${valorFormateado}</td>
                </tr>
            `;
        }
    }
    
    html += '</table></div>';
    return html;
}

async function cargarTablaDatawarehouseCompleta() {
    try {
        const data = await makeRequest('/datos-datawarehouse');
        const tbody = document.getElementById('tabla-datawarehouse-completa');
        
        if (data.proyectos && data.proyectos.length > 0) {
            tbody.innerHTML = data.proyectos.map(p => {
                // Determinar badge de estado según el estado real del proyecto
                let estadoBadge = '<span class="badge bg-secondary">Desconocido</span>';
                if (p.estado) {
                    if (p.estado === 'Completado') {
                        estadoBadge = '<span class="badge bg-success">Completado</span>';
                    } else if (p.estado === 'Cancelado') {
                        estadoBadge = '<span class="badge bg-warning">Cancelado</span>';
                    } else if (p.estado === 'En Progreso') {
                        estadoBadge = '<span class="badge bg-primary">En Progreso</span>';
                    } else if (p.estado === 'Pendiente') {
                        estadoBadge = '<span class="badge bg-info">Pendiente</span>';
                    }
                }
                
                const cumplimientoTiempo = p.cumplimiento_tiempo === 'Sí' || p.cumplimiento_tiempo === 1 ? 
                    '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                    '<span class="badge bg-danger"><i class="fas fa-times"></i></span>';
                    
                const cumplimientoPresup = p.cumplimiento_presupuesto === 'Sí' || p.cumplimiento_presupuesto === 1 ? 
                    '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                    '<span class="badge bg-danger"><i class="fas fa-times"></i></span>';
                
                return `
                    <tr>
                        <td>${p.id_proyecto}</td>
                        <td>${p.nombre_proyecto}</td>
                        <td>${estadoBadge}</td>
                        <td class="text-center">${cumplimientoTiempo}</td>
                        <td>${p.duracion_planificada || 0} días</td>
                        <td>${p.duracion_real || 0} días</td>
                        <td class="text-center">${cumplimientoPresup}</td>
                        <td>${formatCurrency(p.presupuesto)}</td>
                        <td>${formatCurrency(p.costo_real)}</td>
                    </tr>
                `;
            }).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No hay datos en el datawarehouse</td></tr>';
        }
    } catch (error) {
        addLog(` Error cargando tabla datawarehouse: ${error.message}`, 'error');
    }
}

async function cargarAnalisis() {
    try {
        const data = await makeRequest('/datos-datawarehouse');
        
        if (data.metricas) {
            const { metricas } = data;
            
            document.getElementById('metricas-analisis').innerHTML = `
                <div class="row text-center">
                    <div class="col-6 mb-3">
                        <h2 class="text-primary">${metricas.total_proyectos}</h2>
                        <p class="small text-muted">Proyectos Finalizados</p>
                    </div>
                    <div class="col-6 mb-3">
                        <h2 class="text-success">${formatCurrency(metricas.presupuesto_promedio)}</h2>
                        <p class="small text-muted">Presupuesto Promedio</p>
                    </div>
                    <div class="col-6 mb-3">
                        <h2 class="text-warning">${Math.round(metricas.dias_promedio || 0)}</h2>
                        <p class="small text-muted">Días Promedio</p>
                    </div>
                    <div class="col-6 mb-3">
                        <h2 class="text-info">${metricas.proyectos_a_tiempo}</h2>
                        <p class="small text-muted">Proyectos a Tiempo</p>
                    </div>
                </div>
            `;
            
            document.getElementById('analisis-desempeno').innerHTML = `
                <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Tasa de Cumplimiento Temporal:</span>
                        <strong>${metricas.proyectos_a_tiempo} / ${metricas.total_proyectos}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Presupuesto Total Ejecutado:</span>
                        <strong>${formatCurrency(metricas.presupuesto_promedio * metricas.total_proyectos)}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Total de Tareas:</span>
                        <strong>${metricas.total_tareas || 0}</strong>
                    </li>
                </ul>
            `;
        }
    } catch (error) {
        addLog(` Error cargando análisis: ${error.message}`, 'error');
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', async function() {
    addLog('Iniciando dashboard ETL...', 'info');
    
    // Verificar conexión inicial
    await checkStatus();
    
    // Cargar datos iniciales según la sección activa
    if (connectionStatus) {
        await cargarMetricas();
        // Verificar si estamos en la sección Dashboard (la inicial)
        const dashboardSection = document.getElementById('dashboard');
        if (dashboardSection && dashboardSection.style.display !== 'none') {
            // No hacer nada adicional, las métricas ya se cargaron
        }
    }
    
    // Configurar actualizaciones automáticas cada 30 segundos
    setInterval(async () => {
        if (connectionStatus) {
            await checkStatus();
        }
    }, 30000);
    
    addLog('Dashboard listo para usar', 'success');
});

// ========================================
// FUNCIONES DSS - CUBO OLAP
// ========================================

// Variable para controlar acceso PM (simulación)
let tieneAccesoPM = false;

async function cargarDimensionesOLAP() {
    try {
        // Usar nuevo endpoint de filtros disponibles
        const response = await fetch(`${API_BASE}/olap/filtros-disponibles`);
        const data = await response.json();
        
        if (data.success) {
            // Poblar selectores
            const clienteSelect = document.getElementById('filtro-cliente');
            const equipoSelect = document.getElementById('filtro-equipo');
            const anioSelect = document.getElementById('filtro-anio');
            
            // Limpiar y poblar clientes con contador de proyectos
            clienteSelect.innerHTML = '<option value="">Todos los clientes</option>';
            data.filtros.clientes.forEach(cliente => {
                clienteSelect.innerHTML += `<option value="${cliente.id_cliente}">${cliente.nombre_cliente} - ${cliente.sector} (${cliente.total_proyectos} proy.)</option>`;
            });
            
            // Limpiar y poblar equipos con contador de proyectos
            equipoSelect.innerHTML = '<option value="">Todos los equipos</option>';
            data.filtros.equipos.forEach(equipo => {
                equipoSelect.innerHTML += `<option value="${equipo.id_equipo}">${equipo.nombre_equipo} (${equipo.total_proyectos} proy.)</option>`;
            });
            
            // Limpiar y poblar años con contador de proyectos
            anioSelect.innerHTML = '<option value="">Todos los años</option>';
            data.filtros.anios.forEach(anio => {
                anioSelect.innerHTML += `<option value="${anio.anio}">${anio.anio} (${anio.total_proyectos} proy.)</option>`;
            });
            
            // Cargar KPIs ejecutivos - DESHABILITADO
            // await cargarKPIsEjecutivos();
            
            showToast(`Filtros cargados: ${data.filtros.clientes.length} clientes, ${data.filtros.equipos.length} equipos, ${data.filtros.anios.length} años`, 'success');
        }
    } catch (error) {
        console.error('Error cargando dimensiones OLAP:', error);
        showToast('Error cargando dimensiones OLAP', 'error');
    }
}

// FUNCIÓN DESHABILITADA - KPIs Ejecutivos removidos del dashboard
/*
async function cargarKPIsEjecutivos() {
    try {
        const response = await fetch(`${API_BASE}/olap/kpis-ejecutivos`);
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('kpis-ejecutivos-cards');
            container.innerHTML = '';
            
            // Tomar los KPIs más recientes
            const ultimosKpis = data.kpis_temporales[0] || {};
            
            const kpiCards = [
                {
                    titulo: 'Proyectos Activos',
                    valor: ultimosKpis.total_proyectos_periodo || 0,
                    icono: 'fas fa-project-diagram',
                    color: 'primary'
                },
                {
                    titulo: 'Completados',
                    valor: ultimosKpis.proyectos_completados || 0,
                    icono: 'fas fa-check-circle',
                    color: 'success'
                },
                {
                    titulo: 'Presupuesto Total',
                    valor: `$${(ultimosKpis.presupuesto_total_periodo || 0).toLocaleString()}`,
                    icono: 'fas fa-dollar-sign',
                    color: 'info'
                },
                {
                    titulo: 'Eficiencia Estimación',
                    valor: `${(ultimosKpis.eficiencia_estimacion_porcentaje || 0).toFixed(1)}%`,
                    icono: 'fas fa-percentage',
                    color: 'warning'
                }
            ];
            
            kpiCards.forEach(kpi => {
                container.innerHTML += `
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="card metric-card metric-${kpi.color}">
                            <div class="card-body text-center">
                                <i class="${kpi.icono} fa-2x mb-2"></i>
                                <h4>${kpi.valor}</h4>
                                <p class="mb-0">${kpi.titulo}</p>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
    } catch (error) {
        console.error('Error cargando KPIs ejecutivos:', error);
    }
}
*/


async function aplicarFiltrosOLAP() {
    try {
        const clienteId = document.getElementById('filtro-cliente').value;
        const equipoId = document.getElementById('filtro-equipo').value;
        const anio = document.getElementById('filtro-anio').value;
        const nivel = document.getElementById('nivel-agregacion').value;
        
        const params = new URLSearchParams();
        if (clienteId) params.append('cliente_id', clienteId);
        if (equipoId) params.append('equipo_id', equipoId);
        if (anio) params.append('anio', anio);
        params.append('nivel', nivel);
        
        // Usar nuevo endpoint v2 con vistas optimizadas
        const response = await fetch(`${API_BASE}/olap/kpis-v2?${params}`);
        const data = await response.json();
        
        if (data.success) {
            mostrarResultadosOLAP(data.data, nivel);
            showToast(`${data.total_resultados} resultados encontrados (${nivel})`, 'success');
        } else {
            showToast('Error aplicando filtros OLAP: ' + (data.error || data.message), 'error');
        }
    } catch (error) {
        console.error('Error aplicando filtros OLAP:', error);
        showToast('Error aplicando filtros OLAP', 'error');
    }
}

function mostrarResultadosOLAP(datos, nivel) {
    const tabla = document.querySelector('#tabla-olap-resultados');
    const thead = tabla.querySelector('thead tr');
    const tbody = tabla.querySelector('tbody');
    
    tbody.innerHTML = '';
    
    if (!datos || datos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No hay datos disponibles</td></tr>';
        return;
    }
    
    // Actualizar encabezados según nivel
    if (nivel === 'total') {
        thead.innerHTML = `
            <th colspan="3" class="text-center">Nivel</th>
            <th>Total Proyectos</th>
            <th>Completados</th>
            <th>Presupuesto Total</th>
            <th>Costo Real</th>
            <th>Rentabilidad %</th>
            <th>% En Presupuesto</th>
        `;
    } else if (nivel === 'por_cliente') {
        thead.innerHTML = `
            <th>Cliente</th>
            <th>Sector</th>
            <th>-</th>
            <th>Total Proyectos</th>
            <th>Completados</th>
            <th>Presupuesto Total</th>
            <th>Costo Real</th>
            <th>Rentabilidad %</th>
            <th>% En Presupuesto</th>
        `;
    } else if (nivel === 'por_equipo') {
        thead.innerHTML = `
            <th>-</th>
            <th>Equipo</th>
            <th>-</th>
            <th>Total Proyectos</th>
            <th>Completados</th>
            <th>Presupuesto Total</th>
            <th>Costo Real</th>
            <th>Rentabilidad %</th>
            <th>% En Presupuesto</th>
        `;
    } else if (nivel === 'por_tiempo') {
        thead.innerHTML = `
            <th>-</th>
            <th>-</th>
            <th>Año</th>
            <th>Total Proyectos</th>
            <th>Completados</th>
            <th>Presupuesto Total</th>
            <th>Costo Real</th>
            <th>Rentabilidad %</th>
            <th>% En Presupuesto</th>
        `;
    } else { // detallado
        thead.innerHTML = `
            <th>Cliente</th>
            <th>Equipo</th>
            <th>Año</th>
            <th>Proyecto</th>
            <th>Estado</th>
            <th>Presupuesto</th>
            <th>Costo Real</th>
            <th>Rentabilidad %</th>
            <th>En Presupuesto</th>
        `;
    }
    
    // Llenar datos
    datos.forEach(fila => {
        const tr = document.createElement('tr');
        
        // Adaptar columnas según el nivel
        if (nivel === 'total') {
            tr.innerHTML = `
                <td colspan="3" class="text-center fw-bold">TOTAL GENERAL</td>
                <td class="fw-bold">${fila.total_proyectos || 0}</td>
                <td>${fila.proyectos_completados || 0}</td>
                <td>$${(fila.presupuesto_total || 0).toLocaleString('es-MX')}</td>
                <td>$${(fila.costo_total || 0).toLocaleString('es-MX')}</td>
                <td class="text-${(fila.rentabilidad_promedio_porcentaje || 0) >= 10 ? 'success' : 'warning'}">${(fila.rentabilidad_promedio_porcentaje || 0).toFixed(1)}%</td>
                <td>${(fila.porcentaje_en_presupuesto || 0).toFixed(1)}%</td>
            `;
        } else if (nivel === 'por_cliente') {
            tr.innerHTML = `
                <td><strong>${fila.cliente || '–'}</strong></td>
                <td><span class="badge bg-secondary">${fila.sector || '–'}</span></td>
                <td>-</td>
                <td class="fw-bold">${fila.total_proyectos || 0}</td>
                <td>${fila.proyectos_completados || 0}</td>
                <td>$${(fila.presupuesto_total || 0).toLocaleString('es-MX')}</td>
                <td>$${(fila.costo_total || 0).toLocaleString('es-MX')}</td>
                <td class="text-${(fila.rentabilidad_promedio_porcentaje || 0) >= 10 ? 'success' : 'warning'}">${(fila.rentabilidad_promedio_porcentaje || 0).toFixed(1)}%</td>
                <td>${(fila.porcentaje_en_presupuesto || 0).toFixed(1)}%</td>
            `;
        } else if (nivel === 'por_equipo') {
            tr.innerHTML = `
                <td>-</td>
                <td><strong>${fila.equipo || '–'}</strong></td>
                <td>-</td>
                <td class="fw-bold">${fila.total_proyectos || 0}</td>
                <td>${fila.proyectos_completados || 0}</td>
                <td>$${(fila.presupuesto_total || 0).toLocaleString('es-MX')}</td>
                <td>$${(fila.costo_total || 0).toLocaleString('es-MX')}</td>
                <td class="text-${(fila.rentabilidad_promedio_porcentaje || 0) >= 10 ? 'success' : 'warning'}">${(fila.rentabilidad_promedio_porcentaje || 0).toFixed(1)}%</td>
                <td>${(fila.porcentaje_en_presupuesto || 0).toFixed(1)}%</td>
            `;
        } else if (nivel === 'por_tiempo') {
            tr.innerHTML = `
                <td>-</td>
                <td>-</td>
                <td class="fw-bold">${fila.anio || '–'}</td>
                <td class="fw-bold">${fila.total_proyectos || 0}</td>
                <td>${fila.proyectos_completados || 0}</td>
                <td>$${(fila.presupuesto_total || 0).toLocaleString('es-MX')}</td>
                <td>$${(fila.costo_total || 0).toLocaleString('es-MX')}</td>
                <td class="text-${(fila.rentabilidad_promedio_porcentaje || 0) >= 10 ? 'success' : 'warning'}">${(fila.rentabilidad_promedio_porcentaje || 0).toFixed(1)}%</td>
                <td>${(fila.porcentaje_en_presupuesto || 0).toFixed(1)}%</td>
            `;
        } else { // detallado
            const esCompletado = fila.estado === 'Completado';
            const estadoBadge = esCompletado ? 
                '<span class="badge bg-success">Completado</span>' : 
                fila.estado === 'Cancelado' ?
                '<span class="badge bg-danger">Cancelado</span>' :
                '<span class="badge bg-warning">En Progreso</span>';
            
            const enPresupuestoBadge = fila.en_presupuesto === 'Sí' ?
                '<span class="text-success">✓ Sí</span>' :
                fila.en_presupuesto === 'No' ?
                '<span class="text-danger">✗ No</span>' :
                '<span class="text-muted">N/A</span>';
            
            tr.innerHTML = `
                <td><strong>${fila.cliente || '–'}</strong></td>
                <td>${fila.equipo || '–'}</td>
                <td>${fila.anio || '–'}</td>
                <td>${fila.proyecto || '–'}</td>
                <td>${estadoBadge}</td>
                <td>$${(fila.presupuesto || 0).toLocaleString('es-MX')}</td>
                <td>$${(fila.costo_real || 0).toLocaleString('es-MX')}</td>
                <td class="text-${(fila.rentabilidad_porcentaje || 0) >= 10 ? 'success' : (fila.rentabilidad_porcentaje || 0) >= 0 ? 'warning' : 'danger'}">${(fila.rentabilidad_porcentaje || 0).toFixed(1)}%</td>
                <td>${enPresupuestoBadge}</td>
            `;
        }
        tbody.appendChild(tr);
    });
}

// ========================================
// FUNCIONES DSS - BSC/OKR
// ========================================

// Variables globales para almacenar instancias de charts
let chartRadarPerspectivas = null;
let chartDonutObjetivos = null;

async function cargarBSC_OKR() {
    try {
        const response = await fetch(`${API_BASE}/bsc/okr`);
        const data = await response.json();
        
        if (data.success) {
            mostrarVisionEstrategica();
            renderizarGraficosResumen(data.perspectivas);
            mostrarPerspectivasBSC(data.perspectivas);
        } else {
            showToast('Error cargando BSC/OKR: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error cargando BSC/OKR:', error);
        showToast('Error cargando BSC/OKR', 'error');
    }
}

function renderizarGraficosResumen(perspectivas) {
    // Destruir charts anteriores si existen
    if (chartRadarPerspectivas) {
        chartRadarPerspectivas.destroy();
    }
    if (chartDonutObjetivos) {
        chartDonutObjetivos.destroy();
    }

    // Preparar datos para radar chart (avance por perspectiva)
    const labelsPerspectivas = [];
    const dataAvance = [];
    let totalVerde = 0;
    let totalAmarillo = 0;
    let totalRojo = 0;

    Object.keys(perspectivas).forEach(nombrePerspectiva => {
        const perspectiva = perspectivas[nombrePerspectiva];
        labelsPerspectivas.push(nombrePerspectiva);
        dataAvance.push(perspectiva.resumen.avance_promedio || 0);
        
        totalVerde += perspectiva.resumen.objetivos_verde || 0;
        totalAmarillo += perspectiva.resumen.objetivos_amarillo || 0;
        totalRojo += perspectiva.resumen.objetivos_rojo || 0;
    });

    // Radar Chart de Perspectivas
    const ctxRadar = document.getElementById('chart-radar-perspectivas').getContext('2d');
    chartRadarPerspectivas = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: labelsPerspectivas,
            datasets: [{
                label: 'Avance Promedio (%)',
                data: dataAvance,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    pointLabels: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.r.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });

    // Donut Chart de Estado de Objetivos
    const ctxDonut = document.getElementById('chart-donut-objetivos').getContext('2d');
    chartDonutObjetivos = new Chart(ctxDonut, {
        type: 'doughnut',
        data: {
            labels: ['🟢 En Meta (Verde)', '🟡 Atención (Amarillo)', '🔴 Crítico (Rojo)'],
            datasets: [{
                data: [totalVerde, totalAmarillo, totalRojo],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ],
                borderColor: [
                    'rgba(40, 167, 69, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return label + ': ' + value + ' objetivos (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

async function mostrarVisionEstrategica() {
    try {
        const response = await fetch(`${API_BASE}/bsc/vision-estrategica`);
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('vision-componentes');
            container.innerHTML = '';
            
            data.vision_componentes.forEach(componente => {
                const progreso = componente.avance_promedio || 0;
                const colorProgress = progreso >= 70 ? 'success' : progreso >= 50 ? 'warning' : 'danger';
                
                container.innerHTML += `
                    <div class="col-md-4 mb-3">
                        <div class="card h-100">
                            <div class="card-body text-center">
                                <h6 class="fw-bold">${componente.vision_componente}</h6>
                                <div class="progress mb-2">
                                    <div class="progress-bar bg-${colorProgress}" style="width: ${progreso}%">
                                        ${progreso.toFixed(1)}%
                                    </div>
                                </div>
                                <small class="text-muted">${componente.total_objetivos} objetivos</small>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
    } catch (error) {
        console.error('Error cargando visión estratégica:', error);
    }
}

function mostrarPerspectivasBSC(perspectivas) {
    const container = document.getElementById('perspectivas-bsc');
    container.innerHTML = '';
    
    const coloresPerspectivas = {
        'Financiera': 'success',
        'Clientes': 'primary',
        'Procesos Internos': 'info',
        'Aprendizaje y Innovación': 'warning'
    };
    
    const iconosPerspectivas = {
        'Financiera': 'fa-dollar-sign',
        'Clientes': 'fa-users',
        'Procesos Internos': 'fa-cogs',
        'Aprendizaje y Innovación': 'fa-lightbulb'
    };
    
    Object.keys(perspectivas).forEach(nombrePerspectiva => {
        const perspectiva = perspectivas[nombrePerspectiva];
        const color = coloresPerspectivas[nombrePerspectiva] || 'secondary';
        const icono = iconosPerspectivas[nombrePerspectiva] || 'fa-star';
        
        let objetivosHtml = '';
        perspectiva.objetivos.forEach(objetivo => {
            let krsHtml = '';
            
            // Construir KRs desde los campos kr1_, kr2_, kr3_ que vienen en el objetivo
            const krs = [];
            for (let i = 1; i <= 3; i++) {
                const kr_codigo = objetivo[`kr${i}_codigo`];
                if (kr_codigo) {
                    const progreso = objetivo[`kr${i}_progreso`];
                    const valorObs = objetivo[`kr${i}_valor_observado`];
                    const meta = objetivo[`kr${i}_meta`];
                    
                    krs.push({
                        codigo_kr: kr_codigo,
                        kr_nombre: objetivo[`kr${i}_nombre`],
                        unidad_medida: objetivo[`kr${i}_unidad_medida`],
                        meta_objetivo: meta,
                        valor_observado: valorObs,
                        progreso_hacia_meta: progreso,
                        estado_semaforo: progreso === null ? 'Sin datos' : 
                                        progreso >= 70 ? 'Verde' : 
                                        progreso >= 50 ? 'Amarillo' : 'Rojo'
                    });
                }
            }
            
            krs.forEach(kr => {
                const tieneMediciones = kr.valor_observado !== null && kr.valor_observado !== undefined;
                
                const krColor = {
                    'Verde': 'success',
                    'Amarillo': 'warning', 
                    'Rojo': 'danger',
                    'Sin datos': 'secondary'
                }[kr.estado_semaforo] || 'secondary';
                
                const progreso = tieneMediciones ? (kr.progreso_hacia_meta || 0) : 0;
                const progresoTexto = tieneMediciones ? `${progreso.toFixed(0)}%` : '📊 Pendiente';
                const progresoWidth = Math.min(progreso, 100);
                
                const valorObservado = tieneMediciones ? 
                    `<span class="text-primary fw-bold">${kr.valor_observado.toFixed(1)}</span> <small class="text-muted">${kr.unidad_medida || ''}</small>` : 
                    '<span class="text-muted">&ndash;</span>';
                
                const metaObjetivo = kr.meta_objetivo ? 
                    `<span class="text-success fw-bold">${kr.meta_objetivo.toFixed(1)}</span> <small class="text-muted">${kr.unidad_medida || ''}</small>` : 
                    '<span class="text-muted">&ndash;</span>';
                
                // Iconos según el tipo de KR
                let iconoKr = '📊';
                const nombreLower = kr.kr_nombre.toLowerCase();
                if (nombreLower.includes('presupuesto') || nombreLower.includes('costo') || nombreLower.includes('rentabilidad') || nombreLower.includes('margen')) {
                    iconoKr = '💰';
                } else if (nombreLower.includes('tiempo') || nombreLower.includes('días') || nombreLower.includes('duración') || nombreLower.includes('retraso')) {
                    iconoKr = '⏱️';
                } else if (nombreLower.includes('satisfacción') || nombreLower.includes('cliente') || nombreLower.includes('cumplimiento')) {
                    iconoKr = '😊';
                } else if (nombreLower.includes('empleado') || nombreLower.includes('talento') || nombreLower.includes('capacitación')) {
                    iconoKr = '👥';
                } else if (nombreLower.includes('proyecto') || nombreLower.includes('tarea')) {
                    iconoKr = '📋';
                }
                
                krsHtml += `
                    <div class="kr-compact mb-3 p-2 rounded" style="background: linear-gradient(to right, rgba(${
                        krColor === 'success' ? '40, 167, 69' : 
                        krColor === 'warning' ? '255, 193, 7' : 
                        krColor === 'danger' ? '220, 53, 69' : '108, 117, 125'
                    }, 0.05), white);">
                        <div class="d-flex align-items-center justify-content-between mb-2">
                            <small class="fw-bold" style="font-size: 0.85rem;">
                                ${iconoKr} ${kr.kr_nombre}
                            </small>
                            <span class="badge bg-${krColor}" style="font-size: 0.75rem;">${progresoTexto}</span>
                        </div>
                        
                        <div class="row g-2 mb-2">
                            <div class="col-4">
                                <div class="text-center p-2 bg-white border rounded shadow-sm">
                                    <div class="text-muted mb-1" style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px;">📍 Actual</div>
                                    <div style="font-size: 0.9rem;">${valorObservado}</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="text-center p-2 bg-white border rounded shadow-sm">
                                    <div class="text-muted mb-1" style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px;">📈 Progreso</div>
                                    <div style="font-size: 0.9rem;" class="text-${krColor}">
                                        <strong>${progresoTexto}</strong>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="text-center p-2 bg-white border rounded shadow-sm">
                                    <div class="text-muted mb-1" style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px;">🎯 Meta</div>
                                    <div style="font-size: 0.9rem;">${metaObjetivo}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="progress" style="height: 8px; background-color: #e9ecef;">
                            <div class="progress-bar bg-${krColor}" 
                                 style="width: ${progresoWidth}%;" 
                                 role="progressbar"
                                 aria-valuenow="${progresoWidth}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                            </div>
                        </div>
                        
                        ${!tieneMediciones ? `
                            <div class="alert alert-warning mt-2 mb-0 py-1 px-2" style="font-size: 0.75rem;">
                                <i class="fas fa-info-circle me-1"></i>
                                <strong>Sin datos:</strong> Este indicador aún no tiene mediciones registradas
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            const avanceObjetivo = objetivo.avance_objetivo_porcentaje || 0;
            const estadoColor = {
                'Verde': 'success',
                'Amarillo': 'warning',
                'Rojo': 'danger'
            }[objetivo.estado_objetivo] || 'secondary';
            
            // Descripción contextual según el objetivo
            let descripcionObjetivo = objetivo.descripcion || objetivo.objetivo_descripcion || '';
            if (!descripcionObjetivo) {
                descripcionObjetivo = `Monitoreo de indicadores clave para ${objetivo.objetivo_nombre}`;
            }
            
            objetivosHtml += `
                <div class="objetivo-compact mb-3 p-3 border-2 border-${estadoColor} rounded-3 shadow-sm" 
                     style="background: linear-gradient(135deg, rgba(${
                         estadoColor === 'success' ? '40, 167, 69' : 
                         estadoColor === 'warning' ? '255, 193, 7' : 
                         estadoColor === 'danger' ? '220, 53, 69' : '108, 117, 125'
                     }, 0.05), white);">
                    
                    <!-- Encabezado del Objetivo -->
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="flex-grow-1">
                            <h6 class="mb-1 fw-bold d-flex align-items-center" style="font-size: 0.95rem;">
                                <span class="badge bg-${estadoColor} me-2" style="font-size: 0.7rem;">
                                    ${objetivo.codigo_objetivo}
                                </span>
                                <i class="fas fa-bullseye me-1 text-${estadoColor}"></i>
                                ${objetivo.objetivo_nombre}
                            </h6>
                            <p class="text-muted mb-2" style="font-size: 0.75rem; line-height: 1.4;">
                                <i class="fas fa-info-circle me-1"></i>
                                ${descripcionObjetivo}
                            </p>
                        </div>
                        <div class="text-end ms-2">
                            <div class="badge bg-${estadoColor} mb-1" style="font-size: 0.85rem; padding: 0.5rem 0.75rem;">
                                ${avanceObjetivo.toFixed(0)}%
                            </div>
                            <div style="font-size: 0.65rem; color: #6c757d;">
                                <i class="fas fa-user me-1"></i>${objetivo.owner_responsable || '–'}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Progress Bar del Objetivo -->
                    <div class="progress mb-3" style="height: 12px;">
                        <div class="progress-bar bg-${estadoColor}" 
                             style="width: ${avanceObjetivo}%;"
                             role="progressbar"
                             aria-valuenow="${avanceObjetivo}"
                             aria-valuemin="0"
                             aria-valuemax="100">
                            <small class="fw-bold">${avanceObjetivo.toFixed(0)}%</small>
                        </div>
                    </div>
                    
                    <!-- Contador de KRs -->
                    <div class="alert alert-light mb-2 py-1 px-2 d-flex align-items-center justify-content-between" 
                         style="font-size: 0.75rem; border-left: 3px solid var(--bs-${estadoColor});">
                        <span>
                            <i class="fas fa-chart-line me-1"></i>
                            <strong>${krs.length} Indicadores Clave</strong> monitoreando este objetivo
                        </span>
                        <span class="text-${estadoColor}">
                            ${objetivo.estado_objetivo === 'Verde' ? '✅ En Meta' : 
                              objetivo.estado_objetivo === 'Amarillo' ? '⚠️ Requiere Atención' : 
                              '🚨 Crítico'}
                        </span>
                    </div>
                    
                    <!-- KRs -->
                    ${krsHtml}
                </div>
            `;
        });
        
        const avancePromedioPerspectiva = perspectiva.resumen.avance_promedio || 0;
        
        container.innerHTML += `
            <div class="col-12 col-lg-6 mb-3">
                <div class="card h-100 shadow-sm">
                    <div class="card-header bg-${color} text-white py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">
                                <i class="fas ${icono} me-1"></i>
                                ${nombrePerspectiva}
                            </h6>
                            <span class="badge bg-white text-${color} fw-bold">${avancePromedioPerspectiva.toFixed(0)}%</span>
                        </div>
                        <div class="mt-1" style="font-size: 0.7rem;">
                            <span class="me-2">🟢 ${perspectiva.resumen.objetivos_verde || 0}</span>
                            <span class="me-2">🟡 ${perspectiva.resumen.objetivos_amarillo || 0}</span>
                            <span>🔴 ${perspectiva.resumen.objetivos_rojo || 0}</span>
                        </div>
                    </div>
                    <div class="card-body p-2" style="max-height: 600px; overflow-y: auto;">
                        ${objetivosHtml || '<p class="text-muted text-center small py-3">Sin objetivos</p>'}
                    </div>
                </div>
            </div>
        `;
    });
}

// ========================================
// FUNCIONES DSS - PREDICCIÓN RAYLEIGH
// ========================================

function simularAccesoPM() {
    // Simular acceso PM para demo
    tieneAccesoPM = true;
    document.getElementById('alert-acceso-pm').style.display = 'none';
    showToast('Acceso PM simulado activado', 'success');
}

async function verificarAccesoPM() {
    try {
        const headers = {};
        if (tieneAccesoPM) {
            headers['X-ROLE'] = 'pm';
        }
        
        const response = await fetch(`${API_BASE}/prediccion/validar-acceso`, { headers });
        const data = await response.json();
        
        if (data.success) {
            if (data.tiene_acceso) {
                document.getElementById('alert-acceso-pm').style.display = 'none';
                showToast('Acceso autorizado para predicciones', 'success');
            } else {
                document.getElementById('alert-acceso-pm').style.display = 'block';
                showToast('Acceso denegado - se requieren permisos PM', 'warning');
            }
        }
    } catch (error) {
        console.error('Error verificando acceso:', error);
        showToast('Error verificando acceso', 'error');
    }
}

async function generarPrediccionRayleigh() {
    try {
        // Validar acceso
        if (!tieneAccesoPM) {
            showToast('Se requieren permisos de Project Manager', 'warning');
            document.getElementById('alert-acceso-pm').style.display = 'block';
            return;
        }
        
        const tamanioProyecto = parseFloat(document.getElementById('tamanio-proyecto').value);
        const duracionSemanas = parseInt(document.getElementById('duracion-semanas').value);
        const complejidad = document.getElementById('complejidad-proyecto').value;
        const tipoProyecto = document.getElementById('tipo-proyecto').value;
        const esfuerzoTesting = parseFloat(document.getElementById('esfuerzo-testing').value);
        
        // Validaciones
        if (!tamanioProyecto || !duracionSemanas) {
            showToast('Por favor complete todos los campos requeridos', 'warning');
            return;
        }
        
        if (tamanioProyecto <= 0 || duracionSemanas <= 0) {
            showToast('Los valores deben ser positivos', 'warning');
            return;
        }
        
        const headers = { 'Content-Type': 'application/json' };
        if (tieneAccesoPM) headers['X-ROLE'] = 'pm';
        
        const response = await fetch(`${API_BASE}/prediccion/defectos-rayleigh`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                tamanio_proyecto: tamanioProyecto,
                duracion_semanas: duracionSemanas,
                complejidad: complejidad,
                tipo_proyecto: tipoProyecto,
                esfuerzo_testing: esfuerzoTesting,
                guardar_en_dw: true
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarResultadosPrediccion(data);
            showToast('Predicción generada exitosamente', 'success');
        } else {
            showToast('Error generando predicción: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error generando predicción Rayleigh:', error);
        showToast('Error generando predicción', 'error');
    }
}

function mostrarResultadosPrediccion(data) {
    // Mostrar sección de resultados
    document.getElementById('resultados-prediccion').style.display = 'block';
    
    // Resumen ejecutivo con diseño mejorado
    const resumenContainer = document.getElementById('resumen-ejecutivo-cards');
    const resumen = data.resumen_ejecutivo;
    const metricas = data.metricas_proyecto;
    
    // Determinar clase de riesgo
    const riesgoBadgeClass = resumen.nivel_riesgo === 'Alto' ? 'riesgo-badge-alto' : 
                             resumen.nivel_riesgo === 'Medio' ? 'riesgo-badge-medio' : 
                             'riesgo-badge-bajo';
    
    resumenContainer.innerHTML = `
        <div class="col-md-3">
            <div class="card prediccion-metric-card">
                <div class="card-body">
                    <div class="prediccion-icon-circle prediccion-icon-defectos">
                        <i class="fas fa-bug"></i>
                    </div>
                    <div class="prediccion-metric-value">${Math.round(metricas.total_defectos_estimado)}</div>
                    <div class="prediccion-metric-label">Defectos Estimados</div>
                    <small class="text-muted d-block mt-2">
                        <i class="fas fa-info-circle me-1"></i>Total esperado
                    </small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card prediccion-metric-card">
                <div class="card-body">
                    <div class="prediccion-icon-circle prediccion-icon-pico">
                        <i class="fas fa-mountain"></i>
                    </div>
                    <div class="prediccion-metric-value">${Math.round(metricas.tiempo_pico_semanas * 10) / 10}</div>
                    <div class="prediccion-metric-label">Semana Pico</div>
                    <small class="text-muted d-block mt-2">
                        <i class="fas fa-clock me-1"></i>Máxima intensidad
                    </small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card prediccion-metric-card">
                <div class="card-body">
                    <div class="prediccion-icon-circle prediccion-icon-50pct">
                        <i class="fas fa-percentage"></i>
                    </div>
                    <div class="prediccion-metric-value">${Math.round(metricas.defectos_al_50_pct)}</div>
                    <div class="prediccion-metric-label">Defectos al 50%</div>
                    <small class="text-muted d-block mt-2">
                        <i class="fas fa-chart-line me-1"></i>Mitad del ciclo
                    </small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card prediccion-metric-card">
                <div class="card-body">
                    <div class="prediccion-icon-circle prediccion-icon-riesgo">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="prediccion-metric-value">
                        <span class="${riesgoBadgeClass}">${resumen.nivel_riesgo}</span>
                    </div>
                    <div class="prediccion-metric-label">Nivel de Riesgo</div>
                    <small class="text-muted d-block mt-2">
                        <i class="fas fa-shield-alt me-1"></i>${Math.round(resumen.densidad_defectos * 10) / 10} defectos/unidad
                    </small>
                </div>
            </div>
        </div>
    `;
    
    // Generar gráfica de Rayleigh
    generarGraficaRayleigh(data);
    
    // Tabla de predicción semanal con mejoras visuales
    const tbody = document.querySelector('#tabla-prediccion-semanal tbody');
    tbody.innerHTML = '';
    
    const semanaPico = Math.round(metricas.tiempo_pico_semanas);
    
    data.predicciones_semanales.forEach((prediccion, index) => {
        const cronogramaTesting = data.cronograma_testing[index];
        const tr = document.createElement('tr');
        
        // Destacar semana pico
        if (prediccion.semana === semanaPico) {
            tr.classList.add('semana-pico-row');
        }
        
        // Progress bar para porcentaje completado
        const progressBar = `
            <div class="tabla-progress-bar">
                <div class="tabla-progress-fill" style="width: ${prediccion.porcentaje_completado}%"></div>
            </div>
        `;
        
        // Badge de intensidad
        const intensidadBadge = cronogramaTesting?.intensidad_recomendada || 'Baja';
        const badgeClass = intensidadBadge === 'Alta' ? 'bg-danger' : 
                          intensidadBadge === 'Media' ? 'bg-warning' : 'bg-success';
        
        tr.innerHTML = `
            <td class="fw-bold">${prediccion.semana === semanaPico ? '🏔️ ' : ''}Semana ${prediccion.semana}</td>
            <td><strong>${Math.round(prediccion.defectos_esperados_semana * 10) / 10}</strong></td>
            <td class="text-primary"><strong>${Math.round(prediccion.defectos_acumulados * 10) / 10}</strong></td>
            <td>
                ${progressBar}
                <small class="text-muted">${Math.round(prediccion.porcentaje_completado * 10) / 10}%</small>
            </td>
            <td><span class="badge bg-secondary">${Math.round(prediccion.tasa_instantanea * 10000) / 10000}</span></td>
            <td>${Math.round((cronogramaTesting?.esfuerzo_testing_horas || 0) * 10) / 10}h</td>
            <td>
                <span class="badge ${badgeClass}">
                    ${intensidadBadge}
                </span>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
    
    // Actualizar info adicional del chart
    document.getElementById('chart-info-pico').textContent = `Semana ${semanaPico}`;
    document.getElementById('chart-info-total').textContent = Math.round(metricas.total_defectos_estimado);
    document.getElementById('chart-info-semanas').textContent = data.predicciones_semanales.length;
    
    // Scroll hacia los resultados
    document.getElementById('resultados-prediccion').scrollIntoView({ behavior: 'smooth' });
}

// Variable global para almacenar el chart de Rayleigh
let chartRayleighInstance = null;

function generarGraficaRayleigh(data) {
    try {
        const canvas = document.getElementById('chart-rayleigh');
        if (!canvas) {
            console.error('Canvas chart-rayleigh no encontrado');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        // Destruir chart anterior si existe
        if (chartRayleighInstance) {
            chartRayleighInstance.destroy();
        }
        
        const predicciones = data.predicciones_semanales;
        const semanas = predicciones.map(p => p.semana);
        const defectosPorSemana = predicciones.map(p => p.defectos_esperados_semana);
        const defectosAcumulados = predicciones.map(p => p.defectos_acumulados);
        const semanaPico = Math.round(data.metricas_proyecto.tiempo_pico_semanas);
        
        console.log('=== DEBUG CURVA RAYLEIGH ===');
        console.log('Total semanas:', semanas.length);
        console.log('Primera semana:', semanas[0], 'Defectos:', defectosPorSemana[0]);
        console.log('Última semana:', semanas[semanas.length-1], 'Defectos:', defectosPorSemana[semanas.length-1]);
        console.log('Semana pico calculada:', semanaPico);
        console.log('Defecto máximo:', Math.max(...defectosPorSemana));
        console.log('Índice defecto máximo:', defectosPorSemana.indexOf(Math.max(...defectosPorSemana)));
        console.log('============================');
        
        chartRayleighInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: semanas.map(s => `S${s}`),
                datasets: [
                    {
                        label: 'Defectos por Semana (Curva Rayleigh)',
                        data: defectosPorSemana,
                        borderColor: '#dc2626',
                        backgroundColor: 'rgba(220, 38, 38, 0.2)',
                        borderWidth: 4,
                        fill: true,
                        tension: 0.4,  // Curva más suave para ver forma de campana
                        cubicInterpolationMode: 'monotone',  // Interpolación suave
                        yAxisID: 'y',
                        pointRadius: semanas.map(s => s === semanaPico ? 12 : 4),
                        pointBackgroundColor: semanas.map(s => s === semanaPico ? '#f59e0b' : '#dc2626'),
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 14
                    },
                    {
                        label: 'Defectos Acumulados',
                        data: defectosAcumulados,
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3,
                        yAxisID: 'y1',
                        pointRadius: 3,
                        pointBackgroundColor: '#06b6d4',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 1,
                        borderDash: [5, 5]
                    }
                ]
            },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 14,
                            weight: '600'
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 15,
                    titleFont: { size: 15, weight: 'bold' },
                    bodyFont: { size: 14 },
                    bodySpacing: 8,
                    callbacks: {
                        title: function(context) {
                            const semana = context[0].label;
                            const semanaNum = parseInt(semana.replace('S', ''));
                            if (semanaNum === semanaPico) {
                                return `${semana} 🏔️ PICO DE DEFECTOS`;
                            }
                            return semana;
                        },
                        label: function(context) {
                            const valor = Math.round(context.parsed.y * 100) / 100;
                            const label = context.dataset.label;
                            if (label.includes('Rayleigh')) {
                                return `📊 ${label}: ${valor} defectos`;
                            }
                            return `📈 ${label}: ${valor} defectos`;
                        },
                        afterBody: function(context) {
                            const semanaNum = parseInt(context[0].label.replace('S', ''));
                            if (semanaNum === semanaPico) {
                                return ['\n💡 Este es el momento de mayor', 'intensidad de testing.'];
                            }
                            return [];
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '📊 Defectos por Semana (Distribución de Rayleigh)',
                        color: '#dc2626',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        padding: 10
                    },
                    grid: {
                        color: 'rgba(220, 38, 38, 0.15)',
                        lineWidth: 1
                    },
                    ticks: {
                        color: '#dc2626',
                        font: { size: 13, weight: '600' },
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '📈 Defectos Acumulados',
                        color: '#06b6d4',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        padding: 10
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: '#06b6d4',
                        font: { size: 13, weight: '600' }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.08)',
                        lineWidth: 1
                    },
                    ticks: {
                        font: { size: 11, weight: '500' },
                        maxRotation: 45,
                        minRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: 20  // Limitar etiquetas para mejor visualización
                    }
                }
            }
        }
    });
        
        console.log('Chart Rayleigh creado exitosamente');
    } catch (error) {
        console.error('Error generando gráfica Rayleigh:', error);
        showToast('Error al generar la gráfica', 'error');
    }
}

// ========================================
// FUNCIONES ACTUALIZADAS showSection
// ========================================

// Actualizar función showSection para incluir las nuevas secciones
const originalShowSection = window.showSection;
window.showSection = async function(sectionName) {
    // Llamar función original
    if (originalShowSection) {
        originalShowSection(sectionName);
    } else {
        // Implementación básica si no existe
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });
        
        const targetSection = document.getElementById(`section-${sectionName}`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
        
        // Actualizar menú activo
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        event?.target?.closest('.menu-item')?.classList.add('active');
        
        // Actualizar título
        const titles = {
            'dashboard': 'Dashboard Principal',
            'datos-origen': 'Datos de Origen',
            'control-etl': 'Control ETL',
            'datawarehouse': 'DataWarehouse',
            'analisis': 'Análisis de Datos',
            'olap-kpis': 'KPIs OLAP',
            'bsc-okr': 'BSC / OKR',
            'prediccion-rayleigh': 'Predicción de Defectos',
            'trazabilidad': 'Trazabilidad'
        };
        
        const titleElement = document.getElementById('section-title');
        if (titleElement) {
            titleElement.textContent = titles[sectionName] || 'Dashboard';
        }
    }
    
    // Cargar datos específicos según sección
    switch (sectionName) {
        case 'olap-kpis':
            await cargarDimensionesOLAP();
            break;
        case 'bsc-okr':
            await cargarBSC_OKR();
            break;
        case 'prediccion-rayleigh':
            await verificarAccesoPM();
            break;
    }
};

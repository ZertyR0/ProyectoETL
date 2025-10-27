// Configuración de la API
const API_BASE = 'http://localhost:5001';

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
const API_URL = 'http://localhost:5001/api';

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
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }[type] || '📝';
    
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
                addLog('✅ Conexiones establecidas correctamente', 'success');
            } else {
                statusTop.innerHTML = '<i class="fas fa-circle text-danger"></i> Error de conexión';
                addLog('❌ Error en las conexiones', 'error');
            }
        }
        
        // Actualizar cards de estado
        updateStatusCards(status);
        
    } catch (error) {
        connectionStatus = false;
        const statusIndicator = document.getElementById('connection-status');
        statusIndicator.innerHTML = '<i class="fas fa-circle text-danger"></i> Sin conexión';
        addLog(`❌ Error de conexión: ${error.message}`, 'error');
        
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
        
        addLog(`✅ Datos de origen cargados: ${data.proyectos_recientes?.length || 0} proyectos`, 'success');
        
    } catch (error) {
        addLog(`❌ Error cargando datos de origen: ${error.message}`, 'error');
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
        if (dataOrigen && dataOrigen.total_proyectos !== undefined) {
            document.getElementById('total-proyectos-origen').textContent = dataOrigen.total_proyectos;
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
                            <h2 class="text-warning">${Math.round(metricas.duracion_promedio)}</h2>
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
                    const estadoBadge = p.tareas_completadas === p.tareas_total ? 
                        '<span class="badge bg-success">Completado</span>' : 
                        '<span class="badge bg-warning">Cancelado</span>';
                    
                    const cumplimientoTiempo = p.cumplimiento_tiempo === 1 ? 
                        '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                        '<span class="badge bg-danger"><i class="fas fa-times"></i></span>';
                    
                    const cumplimientoPresupuesto = p.cumplimiento_presupuesto === 1 ? 
                        '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                        '<span class="badge bg-danger"><i class="fas fa-times"></i></span>';
                    
                    return `
                        <tr>
                            <td>${p.id}</td>
                            <td><strong>${p.nombre || 'Sin nombre'}</strong></td>
                            <td>${estadoBadge}</td>
                            <td>${cumplimientoTiempo}</td>
                            <td>${p.duracion_plan} días</td>
                            <td>${p.duracion_real} días</td>
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
        
        addLog(`✅ Métricas cargadas: ${dataDW?.proyectos?.length || 0} proyectos en DW`, 'success');
        
    } catch (error) {
        addLog(`❌ Error cargando métricas: ${error.message}`, 'error');
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
        
        addLog(`📊 Generando datos: ${clientes} clientes, ${empleados} empleados, ${equipos} equipos, ${proyectos} proyectos...`, 'info');
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
            addLog(`✅ Datos generados: ${stats.clientes} clientes, ${stats.empleados} empleados, ${stats.equipos} equipos, ${stats.proyectos} proyectos, ${stats.tareas} tareas`, 'success');
            showToast('¡Datos generados exitosamente!', 'success');
            
            // Recargar datos
            await cargarTodasTablasOrigen();
            await checkStatus();
        } else {
            throw new Error(result.message || result.error || 'Error desconocido');
        }
        
    } catch (error) {
        addLog(`❌ Error generando datos: ${error.message}`, 'error');
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
        
        addLog('✅ Datos insertados correctamente', 'success');
        showToast(result.message, 'success');
        
        // Recargar datos
        await checkStatus();
        
    } catch (error) {
        addLog(`❌ Error insertando datos: ${error.message}`, 'error');
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
        
        addLog('🚀 Iniciando proceso ETL...', 'info');
        showToast('Ejecutando proceso ETL...', 'info');
        
        const result = await makeRequest('/ejecutar-etl', {
            method: 'POST'
        });
        
        addLog('✅ Proceso ETL completado exitosamente', 'success');
        addLog(`📊 Registros procesados: ${JSON.stringify(result.registros_procesados)}`, 'info');
        showToast(result.message, 'success');
        
        // Recargar datos
        await cargarMetricas();
        await checkStatus();
        
    } catch (error) {
        addLog(`❌ Error en proceso ETL: ${error.message}`, 'error');
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
        
        addLog('✅ Datos eliminados correctamente', 'success');
        showToast(result.message, 'success');
        
        // Recargar datos
        await cargarMetricas();
        await checkStatus();
        
    } catch (error) {
        addLog(`❌ Error limpiando datos: ${error.message}`, 'error');
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
                                                            return '<td class="text-muted"><em>null</em></td>';
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
        addLog(`❌ Error cargando tabla origen: ${error.message}`, 'error');
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
        addLog(`🔍 Buscando ${tipo} por ${criterio}: ${valor}...`, 'info');
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
        
        addLog(`✅ Búsqueda completada`, 'success');
        
        // Scroll hacia los resultados
        document.getElementById('resultado-trazabilidad').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        addLog(`❌ Error en búsqueda: ${error.message}`, 'error');
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
                valorFormateado = '<span class="text-muted"><em>null</em></span>';
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
                const estadoBadge = p.tareas_completadas === p.tareas_total ? 
                    '<span class="badge bg-success">Completado</span>' : 
                    '<span class="badge bg-warning">Cancelado</span>';
                
                const cumplimientoTiempo = p.cumplimiento_tiempo === 1 ? 
                    '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                    '<span class="badge bg-danger"><i class="fas fa-times"></i></span>';
                    
                const cumplimientoPresup = p.cumplimiento_presupuesto === 1 ? 
                    '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                    '<span class="badge bg-danger"><i class="fas fa-times"></i></span>';
                
                return `
                    <tr>
                        <td>${p.id_proyecto}</td>
                        <td>${p.nombre_proyecto}</td>
                        <td>${estadoBadge}</td>
                        <td class="text-center">${cumplimientoTiempo}</td>
                        <td>${p.duracion_plan} días</td>
                        <td>${p.duracion_real} días</td>
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
        addLog(`❌ Error cargando tabla datawarehouse: ${error.message}`, 'error');
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
                        <h2 class="text-warning">${Math.round(metricas.duracion_promedio)}</h2>
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
        addLog(`❌ Error cargando análisis: ${error.message}`, 'error');
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', async function() {
    addLog('🚀 Iniciando dashboard ETL...', 'info');
    
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
    
    addLog('✅ Dashboard listo para usar', 'success');
});

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

function addLog(message, type = 'info') {
    const logs = document.getElementById('logs');
    const timestamp = new Date().toLocaleTimeString();
    const className = type === 'error' ? 'text-danger' : type === 'success' ? 'text-success' : type === 'warning' ? 'text-warning' : 'text-info';
    
    logs.innerHTML += `<div class="${className}">[${timestamp}] ${message}</div>`;
    logs.scrollTop = logs.scrollHeight;
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
        
        // Actualizar indicador de conexión
        const statusIndicator = document.getElementById('connection-status');
        if (connectionStatus) {
            statusIndicator.innerHTML = '<i class="fas fa-circle text-success"></i> Conectado';
            addLog('✅ Conexiones establecidas correctamente', 'success');
        } else {
            statusIndicator.innerHTML = '<i class="fas fa-circle text-danger"></i> Error de conexión';
            addLog('❌ Error en las conexiones', 'error');
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
        const data = await makeRequest('/datos-datawarehouse');
        
        const container = document.getElementById('metricas-container');
        
        if (data.metricas) {
            const { metricas } = data;
            container.innerHTML = `
                <div class="col-md-3 mb-3">
                    <div class="card text-center border-primary">
                        <div class="card-body">
                            <h2 class="text-primary">${metricas.total_proyectos}</h2>
                            <p class="card-text">Total Proyectos</p>
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
        } else {
            container.innerHTML = `
                <div class="col-12 text-center text-muted">
                    <i class="fas fa-chart-bar fa-3x mb-3"></i>
                    <p>No hay métricas disponibles</p>
                </div>
            `;
        }
        
        addLog('✅ Métricas cargadas correctamente', 'success');
        
    } catch (error) {
        addLog(`❌ Error cargando métricas: ${error.message}`, 'error');
        document.getElementById('metricas-container').innerHTML = `
            <div class="col-12 text-center text-danger">
                <i class="fas fa-exclamation-triangle fa-2x"></i>
                <p>Error cargando métricas</p>
            </div>
        `;
    }
}

// Funciones de control
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
        await cargarDatosOrigen();
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
        await cargarDatosOrigen();
        await cargarMetricas();
        await checkStatus();
        
    } catch (error) {
        addLog(`❌ Error limpiando datos: ${error.message}`, 'error');
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', async function() {
    addLog('🚀 Iniciando dashboard ETL...', 'info');
    
    // Verificar conexión inicial
    await checkStatus();
    
    // Cargar datos iniciales
    if (connectionStatus) {
        await cargarDatosOrigen();
        await cargarMetricas();
    }
    
    // Configurar actualizaciones automáticas cada 30 segundos
    setInterval(async () => {
        if (connectionStatus) {
            await checkStatus();
        }
    }, 30000);
    
    addLog('✅ Dashboard listo para usar', 'success');
});

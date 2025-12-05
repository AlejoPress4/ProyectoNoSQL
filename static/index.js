// JavaScript para la página principal
class MainPageController {
  constructor() {
    this.init();
  }

  init() {
    this.loadStats();
    this.setupEventListeners();
    this.createActionButtons();
  }

  setupEventListeners() {
    // Hacer clickeables los badges de ejemplo de búsqueda
    document.querySelectorAll(".badge-example").forEach((badge) => {
      badge.style.cursor = "pointer";
      badge.addEventListener("click", (e) => {
        const queryText = e.target.textContent.trim().replace(/[""]/g, "");
        this.redirectToSearch(queryText);
      });
    });

    // Hacer las cards de features clickeables
    this.setupFeatureCards();
  }

  setupFeatureCards() {
    const featureCards = document.querySelectorAll(".col-md-4 .card");

    featureCards[0].style.cursor = "pointer";
    featureCards[0].addEventListener("click", () => {
      window.location.href = "/ragtech";
    });

    featureCards[1].style.cursor = "pointer";
    featureCards[1].addEventListener("click", () => {
      this.showProducts();
    });

    featureCards[2].style.cursor = "pointer";
    featureCards[2].addEventListener("click", () => {
      this.showCategories();
    });
  }

  createActionButtons() {
    // Crear botones de acción en la sección de estadísticas
    const statsSection = document.querySelector(
      ".row.g-4.mt-5.pt-5.border-top"
    );

    // Agregar botones de acción después de las estadísticas
    const actionsDiv = document.createElement("div");
    actionsDiv.className = "col-12 text-center mt-4";
    actionsDiv.innerHTML = `
            <div class="btn-group-custom">
                <button class="btn btn-outline-primary me-3" onclick="window.mainController.showProducts()">
                    <i class="fas fa-list me-2"></i>Ver Todos los Productos
                </button>
                <button class="btn btn-outline-success me-3" onclick="window.mainController.showCategories()">
                    <i class="fas fa-tags me-2"></i>Ver Categorías
                </button>
                <button class="btn btn-outline-info" onclick="window.mainController.showApiDocs()">
                    <i class="fas fa-code me-2"></i>API Documentation
                </button>
            </div>
        `;

    statsSection.appendChild(actionsDiv);

    // Hacer los contadores clickeables
    document.getElementById("productos-count").parentElement.style.cursor =
      "pointer";
    document
      .getElementById("productos-count")
      .parentElement.addEventListener("click", () => {
        this.showProducts();
      });

    document.getElementById("categorias-count").parentElement.style.cursor =
      "pointer";
    document
      .getElementById("categorias-count")
      .parentElement.addEventListener("click", () => {
        this.showCategories();
      });
  }

  async loadStats() {
    try {
      console.log("🔄 Cargando estadísticas...");
      const response = await fetch("/api/stats");
      const data = await response.json();

      if (data.status === "success") {
        const stats = data.estadisticas;
        console.log("📊 Estadísticas cargadas:", stats);

        if (stats.productos) {
          document.getElementById("productos-count").textContent =
            stats.productos;
        }
        if (stats.categorias) {
          document.getElementById("categorias-count").textContent =
            stats.categorias;
        }
        if (stats.usuarios) {
          document.getElementById("usuarios-count").textContent =
            stats.usuarios;
        }
        if (stats.resenas) {
          document.getElementById("reviews-count").textContent = stats.resenas;
        }
      }
    } catch (error) {
      console.error("❌ Error cargando estadísticas:", error);
      this.showStatsError();
    }
  }

  showStatsError() {
    document.getElementById("productos-count").textContent = "N/A";
    document.getElementById("categorias-count").textContent = "N/A";
    document.getElementById("usuarios-count").textContent = "N/A";
    document.getElementById("reviews-count").textContent = "N/A";
  }

  redirectToSearch(query) {
    // Redirigir a la página de búsqueda con la consulta pre-cargada
    const searchUrl = `/ragtech?query=${encodeURIComponent(query)}`;
    window.location.href = searchUrl;
  }

  async showProducts() {
    try {
      const response = await fetch("/api/products");
      const data = await response.json();

      if (data.status === "success") {
        this.displayModal(
          "Productos Disponibles",
          this.formatProductsList(data.productos)
        );
      } else {
        this.displayModal("Error", "No se pudieron cargar los productos.");
      }
    } catch (error) {
      console.error("Error:", error);
      this.displayModal("Error", "Error de conexión al cargar productos.");
    }
  }

  async showCategories() {
    try {
      const response = await fetch("/api/categories");
      const data = await response.json();

      if (data.status === "success") {
        this.displayModal(
          "Categorías Disponibles",
          this.formatCategoriesList(data.categorias)
        );
      } else {
        this.displayModal("Error", "No se pudieron cargar las categorías.");
      }
    } catch (error) {
      console.error("Error:", error);
      this.displayModal("Error", "Error de conexión al cargar categorías.");
    }
  }

  showApiDocs() {
    const apiDocs = `
            <div class="text-start">
                <h6><i class="fas fa-search me-2"></i>Endpoints de Búsqueda:</h6>
                <ul>
                    <li><code>GET /ragtech</code> - Interfaz de búsqueda</li>
                    <li><code>POST /ragtech</code> - Búsqueda semántica</li>
                </ul>
                
                <h6><i class="fas fa-database me-2"></i>Endpoints de API:</h6>
                <ul>
                    <li><code>GET /api/products</code> - Todos los productos</li>
                    <li><code>GET /api/categories</code> - Todas las categorías</li>
                    <li><code>GET /api/stats</code> - Estadísticas del sistema</li>
                </ul>
                
                <h6><i class="fas fa-code me-2"></i>Ejemplo de búsqueda POST:</h6>
                <pre><code>{
  "query": "smartphone con buena cámara",
  "limit": 10,
  "include_reviews": true
}</code></pre>
            </div>
        `;
    this.displayModal("Documentación de la API", apiDocs);
  }

  formatProductsList(productos) {
    if (!productos || productos.length === 0) {
      return '<p class="text-muted">No hay productos disponibles.</p>';
    }

    let html = '<div class="row g-3">';
    productos.slice(0, 12).forEach((producto) => {
      html += `
                <div class="col-md-6">
                    <div class="border p-2 rounded">
                        <h6 class="mb-1">${producto.nombre}</h6>
                        <small class="text-muted">${
                          producto.marca?.nombre || "Sin marca"
                        }</small>
                        <div class="d-flex justify-content-between align-items-center mt-1">
                            <span class="badge bg-primary">${
                              producto.categoria?.nombre || "Sin categoría"
                            }</span>
                            <strong>$${
                              producto.precio_usd?.toLocaleString() || "N/A"
                            }</strong>
                        </div>
                    </div>
                </div>
            `;
    });
    html += "</div>";

    if (productos.length > 12) {
      html += `<p class="text-center mt-3"><small class="text-muted">Y ${
        productos.length - 12
      } productos más...</small></p>`;
    }

    return html;
  }

  formatCategoriesList(categorias) {
    if (!categorias || categorias.length === 0) {
      return '<p class="text-muted">No hay categorías disponibles.</p>';
    }

    let html = '<div class="row g-3">';
    categorias.forEach((categoria) => {
      html += `
                <div class="col-md-6">
                    <div class="border p-3 rounded text-center">
                        <h6>${categoria.nombre}</h6>
                        <p class="text-muted small mb-2">${
                          categoria.descripcion || "Sin descripción"
                        }</p>
                        <span class="badge bg-info">${categoria.slug}</span>
                    </div>
                </div>
            `;
    });
    html += "</div>";

    return html;
  }

  displayModal(title, content) {
    // Crear modal si no existe
    let modal = document.getElementById("dynamicModal");
    if (!modal) {
      const modalHTML = `
                <div class="modal fade" id="dynamicModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title"></h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                            </div>
                            <div class="modal-body"></div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
      document.body.insertAdjacentHTML("beforeend", modalHTML);
      modal = document.getElementById("dynamicModal");
    }

    // Actualizar contenido del modal
    modal.querySelector(".modal-title").textContent = title;
    modal.querySelector(".modal-body").innerHTML = content;

    // Mostrar modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
  window.mainController = new MainPageController();
  console.log("✅ Controlador de página principal inicializado");
});

// Agregar estilos CSS dinámicos
const style = document.createElement("style");
style.textContent = `
    .badge-example {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .badge-example:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: scale(1.05);
        transition: transform 0.2s ease;
    }
    
    .btn-group-custom {
        margin-top: 20px;
    }
    
    .btn-group-custom .btn {
        margin: 5px;
    }
    
    @media (max-width: 768px) {
        .btn-group-custom .btn {
            display: block;
            width: 100%;
            margin: 5px 0;
        }
    }
`;
document.head.appendChild(style);

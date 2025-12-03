// JavaScript para la aplicación RAG Tech
class RAGTechSearch {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadingIndicator = document.getElementById("loadingIndicator");
    this.welcomeMessage = document.getElementById("welcomeMessage");
    this.searchResults = document.getElementById("searchResults");
    this.errorMessage = document.getElementById("errorMessage");
    this.searchForm = document.getElementById("searchForm");

    // Cargar consulta desde URL si existe
    this.loadQueryFromURL();
  }

  loadQueryFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get("query");
    if (query) {
      document.getElementById("queryInput").value = query;
      // Ejecutar búsqueda automáticamente después de un breve delay
      setTimeout(() => {
        this.performSearch();
      }, 500);
    }
  }

  setupEventListeners() {
    // Form submission
    document.getElementById("searchForm").addEventListener("submit", (e) => {
      e.preventDefault();
      this.performSearch();
    });

    // Quick examples
    document.querySelectorAll(".quick-example").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const query = e.target.closest("button").getAttribute("data-query");
        document.getElementById("queryInput").value = query;
        this.performSearch();
      });
    });

    // Enter key in textarea
    document.getElementById("queryInput").addEventListener("keydown", (e) => {
      if (e.key === "Enter" && e.ctrlKey) {
        e.preventDefault();
        this.performSearch();
      }
    });
  }

  showLoading() {
    this.welcomeMessage.classList.add("d-none");
    this.searchResults.classList.add("d-none");
    this.errorMessage.classList.add("d-none");
    this.loadingIndicator.classList.remove("d-none");

    // Disable search button
    const searchBtn = document.getElementById("searchBtn");
    searchBtn.disabled = true;
    searchBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i>Buscando...';
  }

  hideLoading() {
    this.loadingIndicator.classList.add("d-none");

    // Re-enable search button
    const searchBtn = document.getElementById("searchBtn");
    searchBtn.disabled = false;
    searchBtn.innerHTML = '<i class="fas fa-search me-2"></i>Buscar';
  }

  showError(message) {
    this.hideLoading();
    this.welcomeMessage.classList.add("d-none");
    this.searchResults.classList.add("d-none");
    this.errorMessage.classList.remove("d-none");
    document.getElementById("errorText").textContent = message;
  }

  async performSearch() {
    const query = document.getElementById("queryInput").value.trim();
    if (!query) {
      alert("Por favor, ingresa una consulta de búsqueda.");
      return;
    }

    this.showLoading();
    const startTime = Date.now();

    try {
      const requestBody = {
        query: query,
        limit: parseInt(document.getElementById("limitSelect").value),
        include_reviews: document.getElementById("includeReviews").checked,
      };

      const response = await fetch("/ragtech", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();

      if (data.status === "success") {
        const searchTime = Date.now() - startTime;
        this.displayResults(data, searchTime);
      } else {
        this.showError(data.error || "Error desconocido en la búsqueda.");
      }
    } catch (error) {
      console.error("Error en la búsqueda:", error);
      this.showError(
        "Error de conexión. Por favor, verifica tu conexión a internet."
      );
    } finally {
      this.hideLoading();
    }
  }

  displayResults(data, searchTime) {
    this.hideLoading();
    this.welcomeMessage.classList.add("d-none");
    this.errorMessage.classList.add("d-none");
    this.searchResults.classList.remove("d-none");

    // Guardar resultados para acceso posterior
    this.lastSearchResults = data.productos;
    this.lastQuery = data.query;

    // Update query info
    document.getElementById("displayQuery").textContent = data.query;
    document.getElementById("totalProducts").textContent = data.total_productos;
    document.getElementById("totalReviews").textContent = data.total_resenas;

    // Update search stats
    const searchStats = document.getElementById("searchStats");
    if (searchStats) {
      document.getElementById("searchTime").textContent = searchTime;
      document.getElementById("analyzedProducts").textContent =
        data.total_productos;
      searchStats.classList.remove("d-none");
    }

    // Display products
    this.displayProducts(data.productos);

    // Display reviews if available
    if (data.resenas && data.resenas.length > 0) {
      this.displayReviews(data.resenas);
    } else {
      document.getElementById("reviewsSection").classList.add("d-none");
    }

    // Smooth scroll to results
    document.getElementById("searchResults").scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  displayProducts(productos) {
    const container = document.getElementById("productsContainer");
    container.innerHTML = "";

    if (!productos || productos.length === 0) {
      container.innerHTML = `
                <div class="col-12 text-center py-4" role="status" aria-live="polite">
                    <i class="fas fa-search fa-3x text-muted mb-3" aria-hidden="true"></i>
                    <h5 class="text-muted">No se encontraron productos</h5>
                    <p class="text-muted">Intenta con una consulta diferente</p>
                </div>
            `;
      return;
    }

    productos.forEach((producto, index) => {
      const productCard = this.createProductCard(producto, index);
      container.appendChild(productCard);
    });
  }

  createProductCard(producto, index) {
    const col = document.createElement("div");
    col.className = "col-md-6 col-lg-4 fade-in-up";
    col.style.animationDelay = `${index * 0.1}s`;

    const similarityColor = this.getSimilarityColor(producto.similarity);
    const availabilityClass = `availability-${producto.disponibilidad}`;
    const brandClass = `brand-${
      producto.marca?.nombre?.toLowerCase().replace(/\s+/g, "") || "default"
    }`;
    const categoryClass = `category-${producto.categoria?.slug || "default"}`;

    col.innerHTML = `
            <div class="card product-card h-100 ${brandClass}" 
                 role="article" 
                 aria-labelledby="product-${index}-title">
                <div class="position-relative">
                    ${this.renderProductImage(producto)}
                    <span class="badge similarity-badge" 
                          style="background-color: ${similarityColor}"
                          role="status"
                          aria-label="Coincidencia semántica: ${Math.round(
                            producto.similarity * 100
                          )} por ciento"
                          title="Relevancia de búsqueda: ${Math.round(
                            producto.similarity * 100
                          )}%">
                        ${Math.round(producto.similarity * 100)}% match
                    </span>
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="badge ${categoryClass} mb-2" 
                              role="status" 
                              aria-label="Categoría: ${
                                producto.categoria?.nombre || "Sin categoría"
                              }">${
      producto.categoria?.nombre || "Sin categoría"
    }</span>
                        <span class="badge ${availabilityClass}" 
                              role="status" 
                              aria-label="Disponibilidad: ${this.formatAvailability(
                                producto.disponibilidad
                              )}">${this.formatAvailability(
      producto.disponibilidad
    )}</span>
                    </div>
                    
                    <h6 class="card-title fw-bold" id="product-${index}-title">${
      producto.nombre
    }</h6>
                    
                    <div class="mb-2">
                        <small class="text-muted" aria-label="Marca: ${
                          producto.marca?.nombre || "Sin marca"
                        }">
                            <i class="fas fa-building me-1" aria-hidden="true"></i>${
                              producto.marca?.nombre || "Sin marca"
                            }
                        </small>
                        <br>
                        <small class="text-muted" aria-label="Código de producto: ${
                          producto.codigo_producto
                        }">
                            <i class="fas fa-barcode me-1" aria-hidden="true"></i>${
                              producto.codigo_producto
                            }
                        </small>
                    </div>
                    
                    <p class="card-text text-muted small" role="text" aria-label="Descripción del producto">
                        ${this.truncateText(producto.descripcion, 200)}
                        ${
                          producto.descripcion &&
                          producto.descripcion.length > 200
                            ? `<button class="btn btn-link btn-sm p-0 ms-2" onclick="window.ragTech.showProductDetails('${producto.id}')">Ver más...</button>`
                            : ""
                        }
                    </p>
                    
                    <!-- Información adicional del producto -->
                    <div class="product-specs mb-2">
                        <small class="text-muted d-block">
                            <i class="fas fa-info-circle me-1" aria-hidden="true"></i>
                            <strong>Código:</strong> ${producto.codigo_producto}
                        </small>
                        ${
                          producto.categoria?.descripcion
                            ? `
                        <small class="text-muted d-block">
                            <i class="fas fa-tag me-1" aria-hidden="true"></i>
                            <strong>Categoría:</strong> ${producto.categoria.descripcion}
                        </small>`
                            : ""
                        }
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center mt-auto">
                        <div class="price-tag" 
                             role="text" 
                             aria-label="Precio: ${
                               producto.precio_usd?.toLocaleString() ||
                               "No disponible"
                             } dólares">
                            <i class="fas fa-dollar-sign" aria-hidden="true"></i>${
                              producto.precio_usd?.toLocaleString() || "N/A"
                            }
                        </div>
                        <div class="rating" 
                             role="group" 
                             aria-label="Calificación: ${
                               producto.calificacion?.toFixed(1) ||
                               "No disponible"
                             } de 5 estrellas">
                            ${this.renderStars(producto.calificacion)}
                            <small class="text-muted">(${
                              producto.calificacion?.toFixed(1) || "N/A"
                            })</small>
                        </div>
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-outline-primary btn-sm w-100" 
                                onclick="window.ragTech.showProductDetails('${
                                  producto.id
                                }', ${producto.similarity})" 
                                title="Ver detalles completos y análisis de coincidencia">
                            <i class="fas fa-eye me-2"></i>Ver Detalles (${Math.round(
                              producto.similarity * 100
                            )}% match)
                        </button>
                    </div>
                </div>
            </div>
        `;

    return col;
  }

  renderProductImage(producto) {
    if (producto.imagen_principal && producto.imagen_principal !== "") {
      return `<img src="${producto.imagen_principal}" 
                   class="card-img-top product-image" 
                   alt="Imagen del producto: ${producto.nombre}" 
                   title="Imagen del ${producto.nombre}"
                   onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="card-img-top product-image" style="display: none;" 
                         role="img" 
                         aria-label="Imagen no disponible para ${producto.nombre}"
                         title="Imagen no disponible">
                        <i class="fas fa-mobile-alt" aria-hidden="true"></i>
                    </div>`;
    } else {
      return `<div class="card-img-top product-image" 
                   role="img" 
                   aria-label="Imagen no disponible para ${producto.nombre}"
                   title="Imagen no disponible">
                        <i class="fas fa-mobile-alt" aria-hidden="true"></i>
                    </div>`;
    }
  }

  displayReviews(resenas) {
    const reviewsSection = document.getElementById("reviewsSection");
    const container = document.getElementById("reviewsContainer");
    container.innerHTML = "";

    if (!resenas || resenas.length === 0) {
      reviewsSection.classList.add("d-none");
      return;
    }

    reviewsSection.classList.remove("d-none");

    resenas.forEach((resena, index) => {
      const reviewCard = this.createReviewCard(resena, index);
      container.appendChild(reviewCard);
    });
  }

  createReviewCard(resena, index) {
    const reviewDiv = document.createElement("div");
    reviewDiv.className = "review-card p-3 mb-3 fade-in-up";
    reviewDiv.style.animationDelay = `${index * 0.1}s`;
    reviewDiv.setAttribute("role", "article");
    reviewDiv.setAttribute("aria-labelledby", `review-${index}-title`);

    const similarityColor = this.getSimilarityColor(resena.similarity);

    reviewDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <h6 class="mb-1" id="review-${index}-title">${
      resena.titulo
    }</h6>
                    <small class="text-muted" 
                           aria-label="Usuario: ${resena.usuario}${
      resena.compra_verificada ? ", Compra verificada" : ""
    }">
                        <i class="fas fa-user me-1" aria-hidden="true"></i>${
                          resena.usuario
                        }
                        ${
                          resena.compra_verificada
                            ? '<i class="fas fa-check-circle text-success ms-2" title="Compra verificada" aria-label="Compra verificada"></i>'
                            : ""
                        }
                    </small>
                </div>
                <div class="text-end">
                    <span class="badge" 
                          style="background-color: ${similarityColor}"
                          role="status"
                          aria-label="Relevancia: ${Math.round(
                            resena.similarity * 100
                          )} por ciento"
                          title="Relevancia de la reseña: ${Math.round(
                            resena.similarity * 100
                          )}%">
                        ${Math.round(resena.similarity * 100)}% relevante
                    </span>
                    <div class="rating-stars mt-1" 
                         role="group" 
                         aria-label="Calificación: ${
                           resena.calificacion
                         } de 5 estrellas">
                        ${this.renderStars(resena.calificacion)}
                    </div>
                </div>
            </div>
            <p class="mb-0 text-dark" role="text" aria-label="Contenido de la reseña">${this.truncateText(
              resena.contenido,
              200
            )}</p>
        `;

    return reviewDiv;
  }

  renderStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    let stars = "";

    for (let i = 0; i < fullStars; i++) {
      stars += '<i class="fas fa-star" aria-hidden="true"></i>';
    }

    if (hasHalfStar) {
      stars += '<i class="fas fa-star-half-alt" aria-hidden="true"></i>';
    }

    for (let i = 0; i < emptyStars; i++) {
      stars += '<i class="far fa-star" aria-hidden="true"></i>';
    }

    return `<span role="img" aria-label="${rating} de 5 estrellas">${stars}</span>`;
  }

  getSimilarityColor(similarity) {
    if (similarity >= 0.8) return "#28a745"; // Verde
    if (similarity >= 0.6) return "#ffc107"; // Amarillo
    if (similarity >= 0.4) return "#fd7e14"; // Naranja
    return "#dc3545"; // Rojo
  }

  formatAvailability(disponibilidad) {
    const availabilityMap = {
      en_stock: "En Stock",
      agotado: "Agotado",
      pre_orden: "Pre-orden",
      descontinuado: "Descontinuado",
    };
    return availabilityMap[disponibilidad] || disponibilidad;
  }

  truncateText(text, maxLength) {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + "...";
  }

  showProductDetails(productId, similarity = null) {
    // Buscar el producto en los últimos resultados
    const producto = this.lastSearchResults?.find((p) => p.id === productId);
    if (!producto) {
      alert("No se encontraron detalles del producto");
      return;
    }

    // Crear contenido del modal con información completa
    const modalContent = `
      <div class="row">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <h5 class="mb-0">${producto.nombre}</h5>
            ${
              similarity
                ? `<span class="badge" style="background-color: ${this.getSimilarityColor(
                    similarity
                  )}; font-size: 1rem;">
              ${Math.round(similarity * 100)}% coincidencia
            </span>`
                : ""
            }
          </div>
          
          <div class="row">
            <div class="col-md-8">
              <h6><i class="fas fa-align-left me-2"></i>Descripción Completa:</h6>
              <div class="bg-light p-3 rounded mb-3" style="max-height: 200px; overflow-y: auto;">
                <p class="mb-0">${
                  producto.descripcion || "Sin descripción disponible"
                }</p>
              </div>
              
              <h6><i class="fas fa-info-circle me-2"></i>Información del Producto:</h6>
              <table class="table table-sm table-striped">
                <tbody>
                  <tr>
                    <td><strong>Código:</strong></td>
                    <td>${producto.codigo_producto || "N/A"}</td>
                  </tr>
                  <tr>
                    <td><strong>Marca:</strong></td>
                    <td>${producto.marca?.nombre || "Sin marca"}</td>
                  </tr>
                  <tr>
                    <td><strong>Categoría:</strong></td>
                    <td>${producto.categoria?.nombre || "Sin categoría"}</td>
                  </tr>
                  <tr>
                    <td><strong>Precio:</strong></td>
                    <td>$${
                      producto.precio_usd?.toLocaleString() || "No disponible"
                    }</td>
                  </tr>
                  <tr>
                    <td><strong>Calificación:</strong></td>
                    <td>
                      ${this.renderStars(producto.calificacion)}
                      <span class="ms-2">(${
                        producto.calificacion?.toFixed(1) || "N/A"
                      })</span>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Disponibilidad:</strong></td>
                    <td>
                      <span class="badge availability-${
                        producto.disponibilidad
                      }">
                        ${this.formatAvailability(producto.disponibilidad)}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="col-md-4">
              ${
                similarity
                  ? `
              <h6><i class="fas fa-chart-line me-2"></i>Análisis de Coincidencia:</h6>
              <div class="bg-primary bg-opacity-10 p-3 rounded mb-3">
                <div class="text-center">
                  <div class="display-6 fw-bold text-primary">${Math.round(
                    similarity * 100
                  )}%</div>
                  <small class="text-muted">Relevancia semántica</small>
                </div>
                <hr>
                <small class="text-muted">
                  <i class="fas fa-lightbulb me-1"></i>
                  Esta coincidencia se basa en la similitud semántica entre tu consulta y la descripción del producto usando embeddings vectoriales.
                </small>
              </div>
              `
                  : ""
              }
              
              <h6><i class="fas fa-cog me-2"></i>Acciones:</h6>
              <div class="d-grid gap-2">
                <button class="btn btn-primary btn-sm" onclick="window.ragTech.searchSimilarProducts('${
                  producto.categoria?.nombre ||
                  producto.marca?.nombre ||
                  producto.nombre
                }')">
                  <i class="fas fa-search me-2"></i>Buscar Similares
                </button>
                <button class="btn btn-outline-secondary btn-sm" onclick="window.ragTech.copyProductInfo('${productId}')">
                  <i class="fas fa-copy me-2"></i>Copiar Información
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.displayModal(`Detalles: ${producto.nombre}`, modalContent);
  }

  searchSimilarProducts(query) {
    document.getElementById("queryInput").value = query;
    // Cerrar modal
    const modal = bootstrap.Modal.getInstance(
      document.getElementById("dynamicModal")
    );
    if (modal) modal.hide();
    // Realizar búsqueda
    this.performSearch();
  }

  copyProductInfo(productId) {
    const producto = this.lastSearchResults?.find((p) => p.id === productId);
    if (!producto) return;

    const info =
      `${producto.nombre}\n` +
      `Marca: ${producto.marca?.nombre || "N/A"}\n` +
      `Precio: $${producto.precio_usd?.toLocaleString() || "N/A"}\n` +
      `Descripción: ${producto.descripcion || "N/A"}`;

    navigator.clipboard.writeText(info).then(() => {
      // Mostrar mensaje de confirmación
      const toast = document.createElement("div");
      toast.className = "toast show position-fixed top-0 end-0 m-3";
      toast.innerHTML =
        '<div class="toast-body">✓ Información copiada al portapapeles</div>';
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 2000);
    });
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

// Initialize the application when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.ragTech = new RAGTechSearch();

  // Add some CSS animations
  const style = document.createElement("style");
  style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out forwards;
            opacity: 0;
        }
    `;
  document.head.appendChild(style);
});

// Utility functions
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    // Could add a toast notification here
    console.log("Copiado al portapapeles:", text);
  });
}

// Add keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Ctrl + / to focus on search input
  if (e.ctrlKey && e.key === "/") {
    e.preventDefault();
    document.getElementById("queryInput").focus();
  }
});

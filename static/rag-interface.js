// JavaScript para la interfaz del Pipeline RAG
class RAGInterface {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.resetPipeline();
  }

  setupEventListeners() {
    // Form submission
    document.getElementById("ragForm").addEventListener("submit", (e) => {
      e.preventDefault();
      this.executeRAGPipeline();
    });

    // Example queries
    document.querySelectorAll(".example-query").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const query = e.target.getAttribute("data-query");
        document.getElementById("ragQuery").value = query;
        this.executeRAGPipeline();
      });
    });
  }

  resetPipeline() {
    // Reset pipeline steps
    document.querySelectorAll(".pipeline-step").forEach((step) => {
      step.classList.remove("active", "complete");
    });

    // Hide results
    document.getElementById("ragResults").style.display = "none";
    document.getElementById("ragLoading").style.display = "none";
    document.getElementById("ragError").style.display = "none";

    // Set first step as active
    document.getElementById("step-input").classList.add("active");
  }

  updatePipelineStep(stepNumber) {
    const steps = [
      "step-input",
      "step-retrieval",
      "step-generation",
      "step-response",
    ];

    // Mark previous steps as complete
    for (let i = 0; i < stepNumber - 1; i++) {
      const step = document.getElementById(steps[i]);
      step.classList.remove("active");
      step.classList.add("complete");
    }

    // Mark current step as active
    if (stepNumber <= 4) {
      const currentStep = document.getElementById(steps[stepNumber - 1]);
      currentStep.classList.remove("complete");
      currentStep.classList.add("active");
    }

    // Mark final step as complete if finished
    if (stepNumber > 4) {
      document.getElementById("step-response").classList.remove("active");
      document.getElementById("step-response").classList.add("complete");
    }
  }

  async executeRAGPipeline() {
    const query = document.getElementById("ragQuery").value.trim();
    if (!query) {
      alert("Por favor, ingresa una pregunta.");
      return;
    }

    try {
      // Reset and show loading
      this.resetPipeline();
      document.getElementById("ragLoading").style.display = "block";
      document.getElementById("ragSubmit").disabled = true;
      document.getElementById("ragSubmit").innerHTML =
        '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';

      // Step 1: Input received
      this.updatePipelineStep(2);
      await this.sleep(800);

      // Prepare request
      const requestData = {
        query: query,
        max_products: parseInt(document.getElementById("maxProducts").value),
        max_reviews: parseInt(document.getElementById("maxReviews").value),
        include_reviews: document.getElementById("includeReviews").checked,
      };

      // Step 2: Retrieval
      console.log("🔍 Iniciando recuperación...", requestData);
      this.updatePipelineStep(3);
      await this.sleep(1000);

      // Execute RAG pipeline
      const response = await fetch("/rag", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (data.status === "success") {
        // Step 3: Generation
        this.updatePipelineStep(4);
        await this.sleep(800);

        // Step 4: Response ready
        this.updatePipelineStep(5);

        // Hide loading and show results
        document.getElementById("ragLoading").style.display = "none";
        this.displayRAGResults(data);
      } else {
        throw new Error(data.error || "Error desconocido en el pipeline RAG");
      }
    } catch (error) {
      console.error("Error en pipeline RAG:", error);
      document.getElementById("ragLoading").style.display = "none";
      this.showError(error.message);
    } finally {
      // Re-enable form
      document.getElementById("ragSubmit").disabled = false;
      document.getElementById("ragSubmit").innerHTML =
        '<i class="fas fa-rocket me-2"></i>Ejecutar Pipeline RAG';
    }
  }

  displayRAGResults(data) {
    // Show results container
    document.getElementById("ragResults").style.display = "block";

    // Display main response
    document.getElementById("ragResponseContent").innerHTML =
      this.formatResponse(data.rag_response);

    // Display metadata
    document.getElementById("modelUsed").textContent = data.metadata.model_used;
    document.getElementById(
      "contextStats"
    ).textContent = `${data.context.total_productos} productos, ${data.context.total_resenas} reseñas`;

    // Display context products
    this.displayContextProducts(data.context.productos);

    // Display context reviews
    this.displayContextReviews(data.context.resenas);

    // Display sources
    this.displaySources(data.sources);

    // Scroll to results
    document.getElementById("ragResults").scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  formatResponse(response) {
    // Convert markdown-like formatting to HTML
    let formatted = response
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/\n/g, "<br>")
      .replace(/#{1,6}\s*(.*?)$/gm, '<h6 class="mt-3 mb-2">$1</h6>')
      .replace(/- (.*?)$/gm, "<li>$1</li>");

    // Wrap lists
    formatted = formatted.replace(/(<li>.*?<\/li>)/gs, "<ul>$1</ul>");

    return formatted;
  }

  displayContextProducts(productos) {
    const container = document.getElementById("contextProducts");
    const count = document.getElementById("productCount");

    count.textContent = productos.length;

    if (productos.length === 0) {
      container.innerHTML =
        '<p class="text-muted">No se encontraron productos relevantes.</p>';
      return;
    }

    container.innerHTML = productos
      .map(
        (producto, index) => `
            <div class="border rounded p-2 mb-2 bg-white">
                <h6 class="mb-1">${producto.nombre}</h6>
                <small class="text-muted">
                    ${producto.marca?.nombre || "Sin marca"} | 
                    $${producto.precio_usd?.toLocaleString() || "N/A"} |
                    ${Math.round(producto.similarity * 100)}% relevancia
                </small>
                <p class="mb-0 small">${this.truncateText(
                  producto.descripcion,
                  100
                )}</p>
            </div>
        `
      )
      .join("");
  }

  displayContextReviews(resenas) {
    const container = document.getElementById("contextReviews");
    const count = document.getElementById("reviewCount");

    count.textContent = resenas.length;

    if (resenas.length === 0) {
      container.innerHTML =
        '<p class="text-muted">No se encontraron reseñas relevantes.</p>';
      return;
    }

    container.innerHTML = resenas
      .map(
        (resena) => `
            <div class="border rounded p-2 mb-2 bg-white">
                <h6 class="mb-1">"${resena.titulo}"</h6>
                <small class="text-muted">
                    ${resena.usuario} | 
                    ${resena.calificacion}/5 estrellas |
                    ${Math.round(resena.similarity * 100)}% relevancia
                </small>
                <p class="mb-0 small">${this.truncateText(
                  resena.contenido,
                  120
                )}</p>
            </div>
        `
      )
      .join("");
  }

  displaySources(sources) {
    const container = document.getElementById("sourcesList");

    if (!sources || sources.length === 0) {
      container.innerHTML =
        '<p class="text-muted">No hay fuentes disponibles.</p>';
      return;
    }

    const sourcesByType = sources.reduce((acc, source) => {
      if (!acc[source.type]) acc[source.type] = [];
      acc[source.type].push(source);
      return acc;
    }, {});

    let html = "";

    if (sourcesByType.product) {
      html += sourcesByType.product
        .map(
          (source) =>
            `<span class="source-badge">
                    <i class="fas fa-mobile-alt me-1"></i>
                    ${source.name} (${Math.round(source.similarity * 100)}%)
                </span>`
        )
        .join("");
    }

    if (sourcesByType.review) {
      html += sourcesByType.review
        .map(
          (source) =>
            `<span class="source-badge">
                    <i class="fas fa-comment me-1"></i>
                    Reseña de ${source.user} (${Math.round(
              source.similarity * 100
            )}%)
                </span>`
        )
        .join("");
    }

    container.innerHTML = html;
  }

  showError(message) {
    document.getElementById("ragError").style.display = "block";
    document.getElementById("errorMessage").textContent = message;

    // Reset pipeline to error state
    document.querySelectorAll(".pipeline-step").forEach((step) => {
      step.classList.remove("active", "complete");
      step.style.background = "#dc3545";
      step.style.color = "white";
    });
  }

  truncateText(text, maxLength) {
    if (!text) return "Sin descripción";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + "...";
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.ragInterface = new RAGInterface();
  console.log("✅ RAG Interface inicializada");
});

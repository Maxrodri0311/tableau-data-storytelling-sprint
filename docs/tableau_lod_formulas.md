# 📊 Tableau Level-of-Detail (LOD) & Calculated Field Catalog
### *Apply on Job — Talent Acquisition & Hiring Analytics*

Este catálogo documenta las expresiones de nivel de detalle (**LOD Expressions: `{FIXED}`, `{INCLUDE}`, `{EXCLUDE}`**) y campos calculados avanzados diseñados para **Tableau Desktop / Tableau Public**, acompañados de su implementación semántica equivalente en **SQL Analítico (Window Functions)**.

---

## 1. Salario Promedio de Mercado por Departamento y Seniority (LOD FIXED)

### 💡 Caso de Uso de Negocio:
Evaluar si la pretensión salarial de un candidato individual excede el promedio histórico de su departamento y nivel de experiencia, independientemente de los filtros activos en la vista (canal, estado de postulación, etc.).

### 📐 Expresión Tableau (LOD FIXED):
```tableau
// Benchmark Salarial Fijo por Rol y Seniority
{ FIXED [Department], [Seniority Level] : AVG([Candidate Expectation USD]) }
```

### ⚙️ Equivalente en SQL Analítico:
```sql
AVG(candidate_expectation_usd) OVER (
    PARTITION BY department, seniority_level
) AS lod_fixed_dept_seniority_avg_salary
```

---

## 2. Varianza de Compensación y Riesgo de Caída de Oferta

### 💡 Caso de Uso de Negocio:
Identificar si el candidato solicita un salario por encima del presupuesto máximo de la vacante para alertar a los reclutadores antes de emitir la oferta formal (*Offer Drop-off Risk*).

### 📐 Expresión Tableau:
```tableau
// Delta Salarial vs Presupuesto Máximo
[Candidate Expectation USD] - [Budget Max USD]

// Clasificación de Riesgo
IF [Candidate Expectation USD] - [Budget Max USD] > 15000 THEN 'HIGH_BUDGET_OVERRUN_RISK'
ELSEIF [Candidate Expectation USD] - [Budget Max USD] > 0 THEN 'MODERATE_OVERRUN'
ELSE 'WITHIN_BUDGET'
END
```

---

## 3. Velocidad de Cierre de Vacante por Canal (LOD FIXED Time-to-Fill)

### 💡 Caso de Uso de Negocio:
Calcular el tiempo promedio en días que toma cada canal de adquisición en cerrar contrataciones para compararlo con el promedio global de la organización.

### 📐 Expresión Tableau (LOD FIXED):
```tableau
// Días Promedio Fijos por Canal de Sourcing
{ FIXED [Sourcing Channel] : AVG([Days In Pipeline]) }
```

### ⚙️ Equivalente en SQL Analítico:
```sql
AVG(days_in_pipeline) OVER (
    PARTITION BY sourcing_channel
) AS lod_fixed_channel_avg_days_to_close
```

---

## 4. Tasa de Conversión de Embudo por Rol (LOD FIXED Conversion Rate)

### 💡 Caso de Uso de Negocio:
Calcular el ratio de éxito de contratación (*Hire Ratio*) por cada perfil técnico evaluado.

### 📐 Expresión Tableau:
```tableau
// Tasa de Contratación por Puesto
SUM([Is Hired]) / COUNT([Application Id])
```

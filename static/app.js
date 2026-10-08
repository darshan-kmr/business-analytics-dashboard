let revenueChart;
let categoryChart;
let orderTypeChart;
let itemsChart;

async function fetchAPI(url) {
    const response=await fetch(url);
    if (!response.ok) {
        throw new Error(
            `API error: ${response.status}`
        );
    }
    return response.json();
}

function getParams() {
    const params=new URLSearchParams();

    const start=document.getElementById("startDate").value;
    const end=document.getElementById("endDate").value;

    const brand=document.getElementById("brand").value;
    const outlet=document.getElementById("outlet").value;
    const category=document.getElementById("category").value;
    const orderType=document.getElementById("orderType").value;
    const settlement=document.getElementById("settlement").value;

    if (start) params.append("start_date", start);
    if (end) params.append("end_date", end);

    if (brand !== "All")
        params.append("brand", brand);

    if (outlet !== "All")
        params.append("outlet", outlet);

    if (category !== "All")
        params.append("category", category);

    if (orderType !== "All")
        params.append("order_type", orderType);

    if (settlement !== "All")
        params.append("settlement", settlement);

    return params.toString();
}

function number(value) {
    return new Intl.NumberFormat(
        "en-IN"
    ).format(Math.round(value || 0));
}

function money(value) {
    return "₹" + number(value);
}

async function loadFilters() {
    const data=await fetchAPI(
        "/api/filters"
    );

    populateSelect(
        "brand",
        data.brands
    );

    populateSelect(
        "outlet",
        data.outlets
    );

    populateSelect(
        "category",
        data.categories
    );

    populateSelect(
        "orderType",
        data.order_types
    );

    populateSelect(
        "settlement",
        data.settlements
    );

    document.getElementById(
        "startDate"
    ).value=data.min_date;

    document.getElementById(
        "endDate"
    ).value=data.max_date;
}

function populateSelect(id, values) {
    const select=document.getElementById(id);

    select.innerHTML=`<option value="All">All</option>`;

    values.forEach(value => {
        const option=document.createElement("option");

        option.value=value;
        option.textContent=value;

        select.appendChild(option);
    });
}

async function loadSummary(query) {
    const data=await fetchAPI(
        `/api/summary?${query}`
    );

    document.getElementById(
        "revenue"
    ).textContent=money(
        data.total_revenue
    );

    document.getElementById(
        "orders"
    ).textContent=number(
        data.total_orders
    );

    document.getElementById(
        "aov"
    ).textContent=money(
        data.average_order_value
    );

    document.getElementById(
        "items"
    ).textContent=number(
        data.total_items
    );

    document.getElementById(
        "records"
    ).textContent=number(
        data.total_records
    );
}

async function loadRevenueChart(query) {
    const data=await fetchAPI(
        `/api/revenue-trend?${query}`
    );

    const labels=data.map(x => x.date);
    const values=data.map(x => x.revenue);

    if (revenueChart) {
        revenueChart.destroy();
    }

    revenueChart=new Chart(
        document.getElementById(
            "revenueChart"
        ),
        {
            type: "line",

            data: {
                labels,

                datasets: [{
                    label: "Revenue",
                    data: values,
                    tension: 0.3,
                    fill: true
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        ticks: {
                            callback: value =>
                                "₹" +
                                number(value)
                        }
                    }
                }
            }
        }
    );
}

async function loadCategoryChart(query) {
    const data=await fetchAPI(
        `/api/revenue-by-category?${query}`
    );

    const labels=data.map(x => x.category);
    const values=data.map(x => x.revenue);

    if (categoryChart) {
        categoryChart.destroy();
    }

    categoryChart=new Chart(
        document.getElementById(
            "categoryChart"
        ),
        {
            type: "bar",

            data: {
                labels,

                datasets: [{
                    label: "Revenue",
                    data: values
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        ticks: {
                            callback: value =>
                                "₹" +
                                number(value)
                        }
                    }
                }
            }
        }
    );
}

async function loadOrderTypeChart(query) {
    const data=await fetchAPI(
        `/api/order-types?${query}`
    );

    const labels=data.map(x => x.order_type);
    const values=data.map(x => x.orders);

    if (orderTypeChart) {
        orderTypeChart.destroy();
    }

    orderTypeChart=new Chart(
        document.getElementById(
            "orderTypeChart"
        ),
        {
            type: "doughnut",

            data: {
                labels,

                datasets: [{
                    data: values
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        }
    );
}

async function loadItemsChart(query) {
    const data=await fetchAPI(
        `/api/top-items?${query}`
    );

    const labels=data.map(x => x.item);
    const values=data.map(x => x.revenue);

    if (itemsChart) {
        itemsChart.destroy();
    }

    itemsChart=new Chart(
        document.getElementById(
            "itemsChart"
        ),
        {
            type: "bar",

            data: {
                labels,

                datasets: [{
                    label: "Revenue",
                    data: values
                }]
            },

            options: {
                indexAxis: "y",

                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    x: {
                        ticks: {
                            callback: value =>
                                "₹" +
                                number(value)
                        }
                    }
                }
            }
        }
    );
}

async function loadDashboard() {
    const status=document.getElementById("status");

    try {
        status.textContent="Updating...";

        const query=getParams();

        await Promise.all([
            loadSummary(query),
            loadRevenueChart(query),
            loadCategoryChart(query),
            loadOrderTypeChart(query),
            loadItemsChart(query)
        ]);

        status.textContent="Live";

    } catch (error) {
        console.error(error);

        status.textContent="Error loading data";
    }
}

function resetFilters() {
    document.getElementById(
        "brand"
    ).value="All";

    document.getElementById(
        "outlet"
    ).value="All";

    document.getElementById(
        "category"
    ).value="All";

    document.getElementById(
        "orderType"
    ).value="All";

    document.getElementById(
        "settlement"
    ).value="All";

    loadFilters().then(
        loadDashboard
    );
}

document
    .getElementById("applyBtn")
    .addEventListener(
        "click",
        loadDashboard
    );

document
    .getElementById("resetBtn")
    .addEventListener(
        "click",
        resetFilters
    );

async function init() {
    try {
        await loadFilters();
        await loadDashboard();
    } catch (error) {
        console.error(error);

        document.getElementById(
            "status"
        ).textContent="Failed to load";
    }
}

init();
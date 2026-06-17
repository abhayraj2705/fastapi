const authArea = document.getElementById("authArea");
const appArea = document.getElementById("appArea");
const loginTab = document.getElementById("loginTab");
const signupTab = document.getElementById("signupTab");
const demoLoginButton = document.getElementById("demoLoginButton");
const signupForm = document.getElementById("signupForm");
const loginForm = document.getElementById("loginForm");
const rentalForm = document.getElementById("rentalForm");
const rentalFormTitle = document.getElementById("rentalFormTitle");
const rentalId = document.getElementById("rentalId");
const propertyName = document.getElementById("propertyName");
const propertyAddress = document.getElementById("propertyAddress");
const tenantName = document.getElementById("tenantName");
const tenantPhone = document.getElementById("tenantPhone");
const startDate = document.getElementById("startDate");
const endDate = document.getElementById("endDate");
const monthlyRent = document.getElementById("monthlyRent");
const paymentStatus = document.getElementById("paymentStatus");
const notes = document.getElementById("notes");
const rentalList = document.getElementById("rentalList");
const userBox = document.getElementById("userBox");
const messageBox = document.getElementById("messageBox");
const activityPanel = document.getElementById("activityPanel");
const logoutButton = document.getElementById("logoutButton");
const refreshButton = document.getElementById("refreshButton");
const cancelEditButton = document.getElementById("cancelEditButton");

let token = localStorage.getItem("rental_token");

function showMessage(message) {
    messageBox.textContent = message;
}

function showJson(data) {
    messageBox.textContent = JSON.stringify(data, null, 2);
}

async function readResponse(response) {
    const contentType = response.headers.get("content-type") || "";

    if (!contentType.includes("application/json")) {
        const text = await response.text();
        console.log("Non JSON response:", text);
        throw new Error(
            `Server returned ${response.status}. Check that the API route is correct.`
        );
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Request failed");
    }

    return data;
}

function getAuthHeaders() {
    return {
        Authorization: `Bearer ${token}`,
    };
}

function updateScreen() {
    if (token) {
        authArea.classList.add("hidden");
        appArea.style.display = "grid";
        activityPanel.style.display = "block";
        logoutButton.style.display = "inline-block";
    } else {
        authArea.classList.remove("hidden");
        appArea.style.display = "none";
        activityPanel.style.display = "none";
        logoutButton.style.display = "none";
        userBox.textContent = "Not logged in.";
        rentalList.innerHTML = "";
    }
}

function showLoginForm() {
    loginForm.classList.remove("hidden");
    signupForm.classList.add("hidden");
    loginTab.classList.add("active");
    signupTab.classList.remove("active");
}

function showSignupForm() {
    signupForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
    signupTab.classList.add("active");
    loginTab.classList.remove("active");
}

function resetRentalForm() {
    rentalId.value = "";
    propertyName.value = "";
    propertyAddress.value = "";
    tenantName.value = "";
    tenantPhone.value = "";
    startDate.value = "";
    endDate.value = "";
    monthlyRent.value = "";
    paymentStatus.value = "Pending";
    notes.value = "";
    rentalFormTitle.textContent = "Add Rental Record";
    cancelEditButton.style.display = "none";
}

async function loadProfile() {
    const response = await fetch("/me", {
        headers: getAuthHeaders(),
    });
    const user = await readResponse(response);
    userBox.textContent = `Logged in as ${user.username}`;
}

async function loadRentals() {
    const response = await fetch("/rentals", {
        headers: getAuthHeaders(),
    });
    const rentals = await readResponse(response);

    rentalList.innerHTML = "";

    if (rentals.length === 0) {
        rentalList.innerHTML = "<p class=\"empty-text\">No rental records saved yet.</p>";
        return;
    }

    rentals.forEach(function (rental) {
        const item = document.createElement("article");
        item.className = "rental-item";

        const details = document.createElement("div");
        const title = document.createElement("h3");
        const status = document.createElement("span");
        const detailGrid = document.createElement("div");
        const address = document.createElement("p");
        const tenant = document.createElement("p");
        const agreement = document.createElement("p");
        const rent = document.createElement("p");
        const recordNotes = document.createElement("p");
        const actions = document.createElement("div");
        const editButton = document.createElement("button");
        const deleteButton = document.createElement("button");

        actions.className = "record-actions";
        detailGrid.className = "record-detail-grid";
        status.className = `status-pill ${rental.payment_status.toLowerCase()}`;
        title.textContent = rental.property_name;
        status.textContent = rental.payment_status;
        address.innerHTML = `<strong>Address</strong><span></span>`;
        tenant.innerHTML = `<strong>Tenant</strong><span></span>`;
        agreement.innerHTML = `<strong>Agreement</strong><span></span>`;
        rent.innerHTML = `<strong>Monthly rent</strong><span></span>`;
        address.querySelector("span").textContent = rental.property_address;
        tenant.querySelector("span").textContent = `${rental.tenant_name} (${rental.tenant_phone || "No phone"})`;
        agreement.querySelector("span").textContent = `${rental.start_date} to ${rental.end_date}`;
        rent.querySelector("span").textContent = rental.monthly_rent;
        recordNotes.textContent = rental.notes || "No notes";
        recordNotes.className = "record-notes";
        editButton.type = "button";
        editButton.textContent = "Edit";
        deleteButton.type = "button";
        deleteButton.className = "danger-button";
        deleteButton.textContent = "Delete";

        details.appendChild(title);
        details.appendChild(status);
        detailGrid.appendChild(address);
        detailGrid.appendChild(tenant);
        detailGrid.appendChild(agreement);
        detailGrid.appendChild(rent);
        details.appendChild(detailGrid);
        details.appendChild(recordNotes);
        actions.appendChild(editButton);
        actions.appendChild(deleteButton);
        item.appendChild(details);
        item.appendChild(actions);

        editButton.addEventListener("click", function () {
            rentalId.value = rental.id;
            propertyName.value = rental.property_name;
            propertyAddress.value = rental.property_address;
            tenantName.value = rental.tenant_name;
            tenantPhone.value = rental.tenant_phone || "";
            startDate.value = rental.start_date;
            endDate.value = rental.end_date;
            monthlyRent.value = rental.monthly_rent;
            paymentStatus.value = rental.payment_status;
            notes.value = rental.notes || "";
            rentalFormTitle.textContent = "Edit Rental Record";
            cancelEditButton.style.display = "inline-block";
        });

        deleteButton.addEventListener("click", async function () {
            await deleteRental(rental.id);
        });

        rentalList.appendChild(item);
    });
}

async function loadDashboard() {
    try {
        await loadProfile();
        await loadRentals();
    } catch (error) {
        showMessage(error.message);
    }
}

signupForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const body = {
        full_name: document.getElementById("signupFullName").value,
        username: document.getElementById("signupUsername").value,
        password: document.getElementById("signupPassword").value,
    };

    try {
        const response = await fetch("/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });
        const data = await readResponse(response);
        showJson(data);
        showMessage("Account created. Login to manage rentals.");
        signupForm.reset();
        showLoginForm();
    } catch (error) {
        showMessage(error.message);
    }
});

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new URLSearchParams();
    formData.append("username", document.getElementById("loginUsername").value);
    formData.append("password", document.getElementById("loginPassword").value);

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: formData,
        });
        const data = await readResponse(response);

        token = data.access_token;
        localStorage.setItem("rental_token", token);

        loginForm.reset();
        updateScreen();
        showMessage("Login successful.");
        await loadDashboard();
    } catch (error) {
        showMessage(error.message);
    }
});

rentalForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const body = {
        property_name: propertyName.value,
        property_address: propertyAddress.value,
        tenant_name: tenantName.value,
        tenant_phone: tenantPhone.value,
        start_date: startDate.value,
        end_date: endDate.value,
        monthly_rent: Number(monthlyRent.value),
        payment_status: paymentStatus.value,
        notes: notes.value,
    };

    const isEditing = rentalId.value !== "";
    const url = isEditing ? `/rentals/${rentalId.value}` : "/rentals";
    const method = isEditing ? "PUT" : "POST";

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
            body: JSON.stringify(body),
        });
        const data = await readResponse(response);

        resetRentalForm();
        showJson(data);
        await loadRentals();
    } catch (error) {
        showMessage(error.message);
    }
});

async function deleteRental(id) {
    try {
        const response = await fetch(`/rentals/${id}`, {
            method: "DELETE",
            headers: getAuthHeaders(),
        });
        const data = await readResponse(response);

        showJson(data);
        await loadRentals();
    } catch (error) {
        showMessage(error.message);
    }
}

refreshButton.addEventListener("click", loadDashboard);

loginTab.addEventListener("click", showLoginForm);

signupTab.addEventListener("click", showSignupForm);

demoLoginButton.addEventListener("click", function () {
    document.getElementById("loginUsername").value = "manager";
    document.getElementById("loginPassword").value = "secret123";
    loginForm.requestSubmit();
});

cancelEditButton.addEventListener("click", function () {
    resetRentalForm();
});

logoutButton.addEventListener("click", function () {
    token = null;
    localStorage.removeItem("rental_token");
    resetRentalForm();
    updateScreen();
    showMessage("Logged out.");
});

updateScreen();
resetRentalForm();

if (token) {
    loadDashboard();
}

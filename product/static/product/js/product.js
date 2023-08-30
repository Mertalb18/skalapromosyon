const localStorage = window.localStorage;

const btnAddProduct = document.getElementById("btn-add-product");
const btnClearProducts = document.getElementById("btn-clear-products");

eventListeners();

function eventListeners() {
    window.addEventListener("load", function () {
        if (window.location.pathname === "/mail-order/") {
            FillDetailTable();
        }

        if (btnAddProduct) {
            btnAddProduct.addEventListener("click", AddCart);
            sendCartItemsToServer();
        };

        if (btnClearProducts) {
            btnClearProducts.addEventListener("click", function () {
                const result = ClearCartItems();
                ShowAlert(result);
            });
        };
    });
}

function AddCart() {
    const productCode = document.getElementById("product-code").innerText;
    const productName = document.getElementById("product-name").innerText;
    const productAmount = parseInt(document.getElementById("product-amount").value);

    const cartItem = {
        productCode: productCode,
        productName: productName,
        productAmount: productAmount,
    };

    const result = UpdateOrAddCartItem(cartItem);
    ShowAlert(result);
}

function FillDetailTable() {
    const carts = GetCartsFromStorage();

    const uniqueCartItems = [];
    const cartItemMap = new Map();

    for (const cart of carts) {
        if (cartItemMap.has(cart.productCode)) {
            cartItemMap.get(cart.productCode).productAmount += cart.productAmount;
        } else {
            cartItemMap.set(cart.productCode, { ...cart });
        }
    }

    cartItemMap.forEach(cart => {
        uniqueCartItems.push(cart);
    });

    const productTable = uniqueCartItems.map((cart, index) => `
        <tr>
            <th scope="row">${index + 1}</th>
            <td>${cart.productCode}</td>
            <td>${cart.productName}</td>
            <td class="text-center">${cart.productAmount}</td>
            <td><i class="fa-solid fa-trash pointer" onclick="DeleteCartItem(${index})"></i></td>
        </tr>
    `).join('');

    document.getElementById("product-order-table").innerHTML = productTable;
}

function GetCartsFromStorage() {
    const cartsJson = localStorage.getItem("carts");
    return cartsJson ? JSON.parse(cartsJson) : [];
}

function UpdateOrAddCartItem(cartItem) {
    const carts = GetCartsFromStorage();
    let updated = false;

    for (let i = 0; i < carts.length; i++) {
        if (carts[i].productCode === cartItem.productCode) {
            carts[i].productAmount = parseInt(carts[i].productAmount) + parseInt(cartItem.productAmount);
            updated = true;
            break;
        }
    }

    if (!updated) {
        carts.push(cartItem);
    }

    localStorage.setItem("carts", JSON.stringify(carts));

    return { success: true, isEmpty: false }; // Return a valid result
}

function DeleteCartItem(index) {
    const carts = GetCartsFromStorage();
    carts.splice(index, 1);
    localStorage.setItem("carts", JSON.stringify(carts));
    
    FillDetailTable();
    const result = {success: true, isEmpty: false};
    ShowAlert(result);
}

function ClearCartItems() {
    const productTable = document.getElementById("product-order-table");

    if (productTable.rows.length === 0) {
        return { success: true, isEmpty: true };
    }

    try {
        localStorage.removeItem("carts");
        productTable.innerHTML = "";
        return { success: false, isEmpty: false };
    } catch (error) {
        console.error("Error clearing cart items:", error);
        return { success: false, isEmpty: true };
    }

}

function ShowAlert(result) {
    const successAlert = document.getElementById("success-alert");
    if (result.success && !result.isEmpty) {
        successAlert.style.display = "block";
    }
    else {
        successAlert.style.display = "block";
        if (result.isEmpty) {
            successAlert.classList.remove("alert-success");
            successAlert.classList.add("alert-danger");
            successAlert.innerHTML = "Liste Zaten Boş";
        }
        else {
            successAlert.innerHTML = "Liste Başarıyla Temizlendi"
        }
    }

    setTimeout(function () {
        successAlert.style.display = "none";
        location.reload();
    }, 3000);
}
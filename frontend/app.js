const API_BASE = "http://18.234.222.177";

function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            localStorage.setItem("email", data.email);
            localStorage.setItem("user_name", data.user_name);
            window.location.href = "main.html";
        } else {
            document.getElementById("message").innerText = "email or password is invalid";
        }
    })
    .catch(() => {
        document.getElementById("message").innerText = "email or password is invalid";
    });
}

function registerUser() {
    const email = document.getElementById("register_email").value;
    const user_name = document.getElementById("register_username").value;
    const password = document.getElementById("register_password").value;

    fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, user_name, password})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = "login.html";
        } else {
            document.getElementById("register_message").innerText = "The email already exists";
        }
    });
}

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}

function loadMainPage() {
    const email = localStorage.getItem("email");
    const user_name = localStorage.getItem("user_name");

    if (!email) {
        window.location.href = "login.html";
        return;
    }

    document.getElementById("user_name").innerText = user_name;
    loadSubscriptions();
}

function queryMusic() {
    const title = document.getElementById("title").value;
    const artist = document.getElementById("artist").value;
    const year = document.getElementById("year").value;
    const album = document.getElementById("album").value;

    const params = new URLSearchParams();

    if (title) params.append("title", title);
    if (artist) params.append("artist", artist);
    if (year) params.append("year", year);
    if (album) params.append("album", album);

    fetch(`${API_BASE}/music/query?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
        const resultsDiv = document.getElementById("results");
        const message = document.getElementById("query_message");

        resultsDiv.innerHTML = "";
        message.innerText = "";

        if (!data.success) {
            message.innerText = data.message || "No result is retrieved. Please query again";
            return;
        }

        data.results.forEach(song => {
            const div = document.createElement("div");
            div.className = "song-card";

            div.innerHTML = `
                <h4>${song.title}</h4>
                <p><strong>Artist:</strong> ${song.artist}</p>
                <p><strong>Year:</strong> ${song.year}</p>
                <p><strong>Album:</strong> ${song.album}</p>
                <img src="${song.image_url}" class="artist-img">
                <button onclick='subscribe(${JSON.stringify(song)})'>Subscribe</button>
            `;

            resultsDiv.appendChild(div);
        });
    });
}

function subscribe(song) {
    const email = localStorage.getItem("email");

    const item = {
        email: email,
        song_id: song.song_id,
        artist: song.artist,
        title: song.title,
        year: song.year,
        album: song.album,
        s3_image_key: song.s3_image_key
    };

    fetch(`${API_BASE}/subscriptions`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(item)
    })
    .then(res => res.json())
    .then(() => {
        loadSubscriptions();
    });
}

function loadSubscriptions() {
    const email = localStorage.getItem("email");

    fetch(`${API_BASE}/subscriptions/${email}`)
    .then(res => res.json())
    .then(data => {
        const subDiv = document.getElementById("subscriptions");
        subDiv.innerHTML = "";

        if (!data.subscriptions || data.subscriptions.length === 0) {
            subDiv.innerText = "No subscriptions yet.";
            return;
        }

        data.subscriptions.forEach(song => {
            const div = document.createElement("div");
            div.className = "song-card";

            div.innerHTML = `
                <h4>${song.title}</h4>
                <p><strong>Artist:</strong> ${song.artist}</p>
                <p><strong>Year:</strong> ${song.year}</p>
                <p><strong>Album:</strong> ${song.album}</p>
                <img src="${song.image_url}" class="artist-img">
                <button onclick='removeSubscription("${song.song_id}")'>Remove</button>
            `;

            subDiv.appendChild(div);
        });
    });
}

function removeSubscription(song_id) {
    const email = localStorage.getItem("email");

    fetch(`${API_BASE}/subscriptions/${email}/${encodeURIComponent(song_id)}`, {
        method: "DELETE"
    })
    .then(res => res.json())
    .then(() => {
        loadSubscriptions();
    });
}

if (window.location.pathname.includes("main.html")) {
    loadMainPage();
}
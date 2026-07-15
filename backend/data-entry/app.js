let teamCount = 0;
let statCount = 0;

// Autocomplete Logic
function autocomplete(inp, arr) {
    let currentFocus;
    inp.addEventListener("input", function(e) {
        let a, b, i, val = this.value;
        closeAllLists();
        if (!val) { return false; }
        currentFocus = -1;
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-list");
        this.parentNode.appendChild(a);
        
        let matchCount = 0;
        for (i = 0; i < arr.length; i++) {
            if (arr[i].toUpperCase().includes(val.toUpperCase())) {
                matchCount++;
                if(matchCount > 20) continue; // max 20 sonuç göster
                
                b = document.createElement("DIV");
                b.setAttribute("class", "autocomplete-item");
                // Match'i kalın yapma
                let startIdx = arr[i].toUpperCase().indexOf(val.toUpperCase());
                b.innerHTML = arr[i].substring(0, startIdx) + "<strong>" + arr[i].substring(startIdx, startIdx + val.length) + "</strong>" + arr[i].substring(startIdx + val.length);
                
                b.innerHTML += "<input type='hidden' value='" + arr[i].replace(/'/g, "&#39;") + "'>";
                b.addEventListener("click", function(e) {
                    inp.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });

    function closeAllLists(elmnt) {
        var x = document.getElementsByClassName("autocomplete-list");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}

function addTeamField() {
    teamCount++;
    const id = `team_${teamCount}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = "p-3 bg-black bg-opacity-30 border border-gray-700 rounded-lg relative";
    div.innerHTML = `
        <button type="button" onclick="document.getElementById('${id}').remove()" class="absolute top-2 right-2 text-red-500 font-bold">X</button>
        <div class="space-y-2 mt-2">
            <div class="autocomplete-wrapper">
                <label class="text-xs text-gray-400">Takım Adı</label>
                <input type="text" id="team_input_${teamCount}" class="input-field team-name" placeholder="Örn: FC Barcelona" required autocomplete="off">
            </div>
            <div class="flex space-x-2">
                <div class="flex-1"><label class="text-xs text-gray-400">Başlangıç Yılı</label><input type="number" class="input-field team-start" placeholder="2003"></div>
                <div class="flex-1"><label class="text-xs text-gray-400">Bitiş Yılı</label><input type="number" class="input-field team-end" placeholder="Boşsa Aktif"></div>
            </div>
        </div>
    `;
    document.getElementById('teamsContainer').appendChild(div);
    
    // Bind autocomplete with imported DB_DATA
    if(typeof DB_DATA !== 'undefined' && DB_DATA.teams) {
        autocomplete(document.getElementById(`team_input_${teamCount}`), DB_DATA.teams);
    }
}

function addStatField() {
    statCount++;
    const id = `stat_${statCount}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = "p-3 bg-black bg-opacity-30 border border-gray-700 rounded-lg relative";
    div.innerHTML = `
        <button type="button" onclick="document.getElementById('${id}').remove()" class="absolute top-2 right-2 text-red-500 font-bold">X</button>
        <div class="space-y-2 mt-2">
            <div>
                <label class="text-xs text-gray-400">Turnuva / Lig Adı</label>
                <select id="league_input_${statCount}" class="input-field stat-league" required>
                    <option value="">Seçiniz...</option>
                    ${typeof DB_DATA !== 'undefined' && DB_DATA.leagues ? DB_DATA.leagues.map(l => `<option value="${l}">${l}</option>`).join('') : ''}
                </select>
            </div>
            <div class="flex space-x-2">
                <div class="flex-1"><label class="text-xs text-gray-400">Maç</label><input type="number" class="input-field stat-apps" value="0"></div>
                <div class="flex-1"><label class="text-xs text-gray-400">Gol</label><input type="number" class="input-field stat-goals" value="0"></div>
                <div class="flex-1"><label class="text-xs text-gray-400">Asist</label><input type="number" class="input-field stat-assists" value="0"></div>
            </div>
            <div class="flex space-x-2">
                <div class="flex-1"><label class="text-xs text-gray-400 text-yellow-500">Sarı Kart</label><input type="number" class="input-field stat-yellow" value="0"></div>
                <div class="flex-1"><label class="text-xs text-gray-400 text-red-500">Kırmızı Kart</label><input type="number" class="input-field stat-red" value="0"></div>
            </div>
        </div>
    `;
    document.getElementById('statsContainer').appendChild(div);
    

}

// Initialize Nationality Select
if(typeof DB_DATA !== 'undefined' && DB_DATA.nationalities) {
    const natSelect = document.getElementById('nationality');
    DB_DATA.nationalities.forEach(n => {
        const opt = document.createElement('option');
        opt.value = n;
        opt.textContent = n;
        if(natSelect) natSelect.appendChild(opt);
    });
}

// Netlify form intercept
document.getElementById('playerForm').addEventListener('submit', function(e) {
    e.preventDefault(); 
    
    // Build JSON object
    const player = {
        known_as: document.getElementById('known_as').value,
        first_name: document.getElementById('first_name').value || null,
        last_name: document.getElementById('last_name').value || null,
        nationality: document.getElementById('nationality').value || null,
        birth_date: document.getElementById('birth_date').value || null,
        height_cm: document.getElementById('height_cm').value ? parseInt(document.getElementById('height_cm').value) : null,
        total_goals: document.getElementById('total_goals').value ? parseInt(document.getElementById('total_goals').value) : 0,
        international_caps: document.getElementById('international_caps').value ? parseInt(document.getElementById('international_caps').value) : 0,
        international_goals: document.getElementById('international_goals').value ? parseInt(document.getElementById('international_goals').value) : 0,
        international_assists: document.getElementById('international_assists').value ? parseInt(document.getElementById('international_assists').value) : 0,
        international_yellow_cards: document.getElementById('international_yellow_cards').value ? parseInt(document.getElementById('international_yellow_cards').value) : 0,
        international_red_cards: document.getElementById('international_red_cards').value ? parseInt(document.getElementById('international_red_cards').value) : 0,
        position: document.getElementById('position').value || null,
        image_url: null, // Fotoğraf alanı kaldırıldığı için null gönderiyoruz.
        team_history: [],
        stats: []
    };

    // Parse Teams
    document.querySelectorAll('#teamsContainer > div').forEach(div => {
        const name = div.querySelector('.team-name').value;
        const start = div.querySelector('.team-start').value;
        const end = div.querySelector('.team-end').value;
        if(name) {
            player.team_history.push({
                team_name: name,
                start_year: start ? parseInt(start) : null,
                end_year: end ? parseInt(end) : null
            });
        }
    });

    // Parse Stats
    document.querySelectorAll('#statsContainer > div').forEach(div => {
        const leagueInput = div.querySelector('.stat-league').value;
        const apps = div.querySelector('.stat-apps').value;
        const goals = div.querySelector('.stat-goals').value;
        const assists = div.querySelector('.stat-assists').value;
        const yellow = div.querySelector('.stat-yellow').value;
        const red = div.querySelector('.stat-red').value;
        
        if(leagueInput) {
            // Örn: "Süper Lig (TR1)" -> "TR1"
            const match = leagueInput.match(/\(([^)]+)\)$/);
            const leagueCode = match ? match[1] : leagueInput;

            player.stats.push({
                league_name: leagueCode,
                appearances: apps ? parseInt(apps) : 0,
                goals: goals ? parseInt(goals) : 0,
                assists: assists ? parseInt(assists) : 0,
                yellow_cards: yellow ? parseInt(yellow) : 0,
                red_cards: red ? parseInt(red) : 0
            });
        }
    });

    const jsonString = JSON.stringify(player, null, 2);
    document.getElementById('json_data').value = jsonString;

    const formData = new FormData(this);
    
    fetch("/", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(formData).toString(),
    })
      .then(() => {
        document.getElementById('successMsg').classList.remove('hidden');
        document.getElementById('playerForm').reset();
        document.getElementById('teamsContainer').innerHTML = '';
        document.getElementById('statsContainer').innerHTML = '';
        teamCount = 0;
        statCount = 0;
        window.scrollTo(0, 0);
      })
      .catch((error) => alert("Hata oluştu: " + error));
});

// Add one empty team and stat field on startup
addTeamField();
addStatField();

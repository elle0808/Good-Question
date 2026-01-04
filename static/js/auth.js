// 1. Supabase 設定
const supabaseUrl = 'https://scffeynwqeksxkvhlcig.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNjZmZleW53cWVrc3hrdmhsY2lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3MjQzNTYsImV4cCI6MjA3ODMwMDM1Nn0.WL-nj6qwZ2UHSdUzhp-Piat10PtHnrfnARGw0Ivo-dA';
const _supabase = supabase.createClient(supabaseUrl, supabaseKey);

// 2. 登入功能
async function handleLogin() {
    const emailEl = document.getElementById('username');
    const passwordEl = document.getElementById('password');

    if (!emailEl || !passwordEl) return;

    const email = emailEl.value;
    const password = passwordEl.value;

    try {
        const { data, error } = await _supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;

        alert("登入成功！");
        localStorage.setItem('supabase_token', data.session.access_token);
        location.reload();
    } catch (error) {
        alert("登入失敗: " + error.message);
    }
}

// 3. 註冊功能 (包含同步到後端)
async function handleRegister() {
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    if (!username || !email || !password) {
        alert("所有欄位都要填寫喔！");
        return;
    }

    try {
        // 第一步：在 Supabase 註冊帳號
        const { data, error } = await _supabase.auth.signUp({
            email,
            password,
            options: {
                // 這是存入 Supabase Auth 內部的方法
                data: {
                    display_name: username
                }
            }
        });
        if (error) throw error;
        if (!data.user) throw new Error("註冊失敗，請稍後再試");

        // 第二步：立刻把 ID 和暱稱傳給 FastAPI 同步
        const syncResponse = await fetch('/api/posts/sync_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: data.user.id,
                username: username,
                email: email
            })
        });

        if (syncResponse.ok) {
            alert(`註冊成功！歡迎你，${username}`);
            // 註冊完通常 Supabase 會自動登入，所以直接整理頁面
            location.reload();
        } else {
            console.error("同步後端失敗");
            alert("帳號已建立，但本地資料同步失敗，請嘗試登入。");
        }
    } catch (error) {
        alert("註冊失敗: " + error.message);
    }
}

// 4. 登出功能
async function handleLogout() {
    await _supabase.auth.signOut();
    localStorage.removeItem('supabase_token');
    alert("已登出");
    location.reload();
}

// 5. 檢查狀態
async function checkUserStatus() {
    try {
        const { data: { user } } = await _supabase.auth.getUser();
        const authArea = document.getElementById('auth-area');

        if (user && authArea) {
            const displayName = user.user_metadata?.display_name || user.email.split('@')[0];

            authArea.innerHTML = `
            <div class="flex items-center pl-3 space-x-3 border-l-2 border-[#f79c33cc]">
                <span class="text-[#854D0C] font-['Roboto:Regular',sans-serif]">你好, ${displayName}</span>
                <button onclick="handleLogout()" 
                        class="bg-[#F79C33] text-white px-4 py-1.5 rounded-lg hover:bg-[#F9BB48] duration-300 transition">
                    登出
                </button>
            </div>
            `;
        }
    } catch (e) {
        console.log("訪客狀態");
    }
}

document.addEventListener('DOMContentLoaded', checkUserStatus);
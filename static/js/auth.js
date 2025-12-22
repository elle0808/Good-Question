// auth.js
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'

// 1. 初始化 Supabase (請替換成你的資訊)
const SUPABASE_URL = 'https://你的專案ID.supabase.co';
const SUPABASE_ANON_KEY = '你的金鑰';
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 2. 封裝登入功能
export async function login(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password,
    });
    return { data, error };
}

// 3. 檢查使用者狀態並更新 UI
export async function checkAuthState(onLogin, onLogout) {
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
        if (onLogin) onLogin(user);
    } else {
        if (onLogout) onLogout();
    }
}
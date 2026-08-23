SHOPSNEAK_HTML_STEP1 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ShopSneak - Quantum Noise-Cancelling Headphones</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 font-sans p-8">
    <div class="max-w-4xl mx-auto bg-white p-6 border border-gray-300">
        <div class="border-b pb-4 mb-6 flex justify-between items-center">
            <h1 class="text-2xl font-bold tracking-tight text-gray-900">ShopSneak Store</h1>
            <span class="text-xs bg-red-100 text-red-800 px-3 py-1 font-bold">LIMITED HACKATHON DEMO SITE</span>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
                <div class="w-full h-64 bg-gray-200 flex items-center justify-center text-gray-500 font-mono">
                    [Product Image: Quantum ANC Pro]
                </div>
                <div class="mt-4 bg-amber-50 border border-amber-200 p-3 flex items-center gap-2 urgency-badge">
                    <span class="text-red-600 font-bold">🔥 HIGH DEMAND:</span>
                    <span class="text-sm text-gray-700">Only 2 left in stock — 48 people viewing this right now!</span>
                </div>
            </div>
            
            <div>
                <h2 class="text-xl font-bold text-gray-900">Quantum ANC Headphones Pro</h2>
                <div class="text-3xl font-extrabold text-blue-600 mt-2">$89.00</div>
                <p class="text-sm text-gray-500 mt-2">Active noise cancellation, 40h battery, ultra-lightweight studio fit.</p>
                
                <!-- Sneaky Pre-checked Addon -->
                <div class="mt-6 p-4 border border-blue-200 bg-blue-50/50">
                    <label class="flex items-start gap-3 cursor-pointer">
                        <input type="checkbox" checked name="warranty" class="mt-1 h-5 w-5 text-blue-600 rounded" />
                        <div>
                            <span class="font-bold text-sm text-gray-900">Add 2-Year Full Accidental Damage Protection Plan</span>
                            <div class="text-xs text-blue-700 font-semibold mt-0.5">+$18.99 (Pre-selected for your protection)</div>
                        </div>
                    </label>
                </div>
                
                <!-- Sneaky Auto-renew Membership -->
                <div class="mt-3 p-3 border border-gray-200 bg-gray-50">
                    <label class="flex items-start gap-3 cursor-pointer">
                        <input type="checkbox" checked name="vip_membership" class="mt-1 h-4 w-4 text-blue-600" />
                        <div>
                            <span class="text-xs font-semibold text-gray-800">Enroll in VIP Express Prime Club</span>
                            <div class="text-[10px] text-gray-500">$9.99/month recurring after 14-day trial</div>
                        </div>
                    </label>
                </div>
                
                <a href="/mock/shopsneak/checkout" class="mt-6 block text-center bg-blue-600 text-white font-bold py-3.5 px-6 uppercase tracking-wider hover:bg-blue-700">
                    Proceed to Instant Checkout →
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""

SHOPSNEAK_HTML_STEP2 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ShopSneak - Order Review & Checkout</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 font-sans p-8">
    <div class="max-w-2xl mx-auto bg-white p-6 border border-gray-300">
        <!-- Fake Resetting Timer -->
        <div class="deal-countdown-timer bg-red-600 text-white p-3 text-center mb-6 font-bold tracking-wide">
            ⚠️ CART RESERVED FOR <span id="timer" class="font-mono text-xl underline">04:59</span> — COMPLETE NOW BEFORE ITEMS RELEASE
        </div>
        
        <h2 class="text-xl font-bold border-b pb-3 mb-4">Step 2: Payment & Final Review</h2>
        
        <div class="space-y-3 text-sm">
            <div class="flex justify-between">
                <span>Quantum ANC Headphones Pro</span>
                <span class="font-semibold">$89.00</span>
            </div>
            <div class="flex justify-between text-blue-800">
                <span>2-Year Accidental Warranty (Pre-selected)</span>
                <span class="font-semibold">$18.99</span>
            </div>
            <!-- Drip Fees added late -->
            <div class="flex justify-between text-red-700 drip-fee-row">
                <span>Platform Regulatory & Convenience Fee</span>
                <span class="font-semibold">$7.50</span>
            </div>
            <div class="flex justify-between text-red-700 drip-fee-row">
                <span>Mandatory Studio Handling Surcharge</span>
                <span class="font-semibold">$4.85</span>
            </div>
            <div class="border-t pt-3 flex justify-between text-lg font-bold checkout-final-total">
                <span>Total Due Now</span>
                <span class="text-2xl text-red-600 font-extrabold">$120.34</span>
            </div>
        </div>
        
        <!-- Illegible low-contrast terms -->
        <div class="mt-6 p-2 bg-gray-100 hidden-disclosure">
            <p style="color: #c4c4c4; font-size: 9px; line-height: 1.2;">
                By placing this order, you agree to recurring annual membership auto-renews at $119/year unless cancelled by certified registered mail 30 days prior. Non-refundable.
            </p>
        </div>
        
        <div class="mt-6 flex flex-col gap-3">
            <button class="w-full bg-blue-600 text-white font-bold py-4 text-center hover:bg-blue-700 primary-upsell">
                AUTHORIZE PAYMENT ($120.34)
            </button>
            <a href="/mock/shopsneak" class="text-xs text-center text-gray-400 hover:text-gray-600 subtle-link">
                No thanks, I don't want to save money and prefer paying full price
            </a>
        </div>
    </div>
    
    <script>
        // Fake timer that resets to 04:59
        let sec = 299;
        setInterval(() => {
            if(sec > 0) sec--;
            const m = String(Math.floor(sec / 60)).padStart(2, '0');
            const s = String(sec % 60).padStart(2, '0');
            document.getElementById('timer').innerText = m + ':' + s;
        }, 1000);
    </script>
</body>
</html>
"""

GYMTRAP_HTML_SIGNUP = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GymTrap SaaS - 1-Click Free Trial</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white text-gray-900 font-sans flex items-center justify-center min-h-screen p-6">
    <div class="max-w-md w-full border border-gray-300 p-8 shadow-sm text-center">
        <h1 class="text-3xl font-extrabold text-black">GymTrap Elite</h1>
        <p class="text-gray-600 mt-2 text-sm">Instant access to 500+ workout programs & calorie tracker.</p>
        <div class="my-6 p-4 bg-green-50 border border-green-200">
            <span class="text-2xl font-bold text-green-700">100% Free 7-Day Trial</span>
            <div class="text-xs text-gray-500 mt-1">1-Click Signup · Instant Activation</div>
        </div>
        <a href="/mock/gymtrap/dashboard" class="block w-full bg-blue-600 text-white font-bold py-3.5 hover:bg-blue-700">
            START 1-CLICK FREE TRIAL NOW →
        </a>
    </div>
</body>
</html>
"""

GYMTRAP_HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GymTrap SaaS - Member Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 text-gray-900 font-sans p-8">
    <div class="max-w-4xl mx-auto bg-white p-6 border border-gray-300">
        <div class="flex justify-between items-center border-b pb-4">
            <h1 class="text-xl font-bold">GymTrap Dashboard</h1>
            <span class="text-xs bg-green-100 text-green-800 px-2 py-1 font-semibold">Active Plan ($49/mo)</span>
        </div>
        <div class="py-8 text-center text-gray-600">
            <h2 class="text-lg font-semibold">Welcome back, Athlete!</h2>
            <p class="text-sm mt-1">Your workouts and meal logs are synced.</p>
        </div>
        <div class="border-t pt-4 flex justify-end">
            <a href="/mock/gymtrap/cancel-1" class="text-xs text-gray-400 hover:text-gray-600 underline">
                Manage / Cancel Membership
            </a>
        </div>
    </div>
</body>
</html>
"""

GYMTRAP_HTML_CANCEL_1 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GymTrap - Cancel Step 1 of 4</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 font-sans p-8">
    <div class="max-w-xl mx-auto bg-white p-8 border border-red-200 cancel-flow-step">
        <div class="text-xs font-bold text-red-600 tracking-wider uppercase mb-2">Cancellation Step 1 of 4</div>
        <h2 class="text-2xl font-bold text-gray-900">Are you sure you want to surrender your progress?</h2>
        <p class="text-sm text-gray-600 mt-2">
            If you cancel today, all your personalized workout plans, streak multipliers, and meal records will be permanently deleted forever.
        </p>
        <div class="my-6 p-4 bg-amber-50 border border-amber-300 text-amber-900 text-xs">
            ⚠️ 87% of members who pause or cancel report regressing to old habits within 14 days.
        </div>
        <div class="flex flex-col gap-3">
            <a href="/mock/gymtrap/dashboard" class="block w-full bg-blue-600 text-white font-bold py-3.5 text-center primary-upsell">
                Keep My Membership & Stay Healthy
            </a>
            <a href="/mock/gymtrap/cancel-2" class="text-xs text-center text-gray-400 hover:text-gray-700 py-2 decline-offer subtle-link">
                No thanks, I don't care about my health and want to give up my discount
            </a>
        </div>
    </div>
</body>
</html>
"""

GYMTRAP_HTML_CANCEL_2 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GymTrap - Cancel Step 2 of 4</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 font-sans p-8">
    <div class="max-w-xl mx-auto bg-white p-8 border border-gray-300 cancel-flow-step">
        <div class="text-xs font-bold text-red-600 tracking-wider uppercase mb-2">Cancellation Step 2 of 4</div>
        <h2 class="text-xl font-bold text-gray-900">Exclusive One-Time Retention Grant</h2>
        <p class="text-sm text-gray-600 mt-2">
            Because we value you, we have credited an immediate 70% discount ($14.99/mo instead of $49/mo) to your profile.
        </p>
        <div class="my-6 p-4 bg-green-50 border border-green-300 text-center">
            <div class="text-2xl font-black text-green-700">70% OFF FOREVER</div>
            <div class="text-xs text-gray-500">Apply this grant with one click.</div>
        </div>
        <div class="flex flex-col gap-3">
            <a href="/mock/gymtrap/dashboard" class="block w-full bg-green-600 text-white font-bold py-3.5 text-center">
                CLAIM 70% DISCOUNT & STAY
            </a>
            <a href="/mock/gymtrap/cancel-3" class="text-xs text-center text-gray-400 hover:text-gray-700 py-2 subtle-link">
                No, I prefer to pay full price elsewhere
            </a>
        </div>
    </div>
</body>
</html>
"""

GYMTRAP_HTML_CANCEL_3 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GymTrap - Cancel Step 3 of 4</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 font-sans p-8">
    <div class="max-w-xl mx-auto bg-white p-8 border border-gray-300 cancel-flow-step">
        <div class="text-xs font-bold text-red-600 tracking-wider uppercase mb-2">Cancellation Step 3 of 4</div>
        <h2 class="text-xl font-bold text-gray-900">Mandatory Exit Interview</h2>
        <p class="text-sm text-gray-600 mt-2">
            Please complete this mandatory 8-question evaluation before cancellation routing.
        </p>
        <div class="space-y-3 my-4 text-xs">
            <label class="block">
                <span class="font-semibold text-gray-700">Why are you leaving us today?</span>
                <select class="mt-1 block w-full border border-gray-300 p-2">
                    <option>Too expensive</option>
                    <option>Achieved fitness goal</option>
                    <option>Switching to local gym</option>
                </select>
            </label>
        </div>
        <div class="flex flex-col gap-3">
            <a href="/mock/gymtrap/dashboard" class="block w-full bg-blue-600 text-white font-bold py-3 text-center">
                Return to Dashboard
            </a>
            <a href="/mock/gymtrap/cancel-4" class="text-xs text-center text-gray-400 hover:text-gray-700 py-2 subtle-link">
                Proceed to Final Confirmation
            </a>
        </div>
    </div>
</body>
</html>
"""

GYMTRAP_HTML_CANCEL_4 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GymTrap - Cancel Step 4: Final Wall</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 font-sans p-8">
    <div class="max-w-xl mx-auto bg-white p-8 border border-red-300 call-support-wall cancel-flow-step">
        <div class="text-xs font-bold text-red-600 tracking-wider uppercase mb-2">Step 4 of 4: Account Security Protocol</div>
        <h2 class="text-2xl font-bold text-gray-900">Phone Verification Required</h2>
        <p class="text-sm text-gray-700 mt-3">
            To prevent unauthorized account closure, online cancellation is disabled for your security. Please call our membership verification specialists:
        </p>
        <div class="my-6 p-4 bg-gray-100 border border-gray-300 text-center">
            <div class="text-xl font-mono font-bold text-red-600">📞 1-800-555-0199</div>
            <div class="text-xs text-gray-500 mt-1">Available Mon–Fri 9:00 AM – 4:30 PM EST (Average wait: 35 mins)</div>
        </div>
        <a href="/mock/gymtrap/dashboard" class="block w-full bg-blue-600 text-white font-bold py-3 text-center">
            Keep Active & Return to Home
        </a>
    </div>
</body>
</html>
"""


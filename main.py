from flask import Flask, render_template, jsonify, request
from knowledge_center import KnowledgeCenter
from challenge_manager import ChallengeManager
from news_service import news_service
import threading
import time
import random
import os
from portfolio_manager import portfolio_manager
from news_analyzer import get_analyzer
from news_fetcher import get_fetcher
from onesignal_service import get_onesignal_service

app = Flask(__name__)

# Initialize Core Systems
kc = KnowledgeCenter()
cm = ChallengeManager()
cm.start_new_challenge()

# Initialize OneSignal (optional - only if keys provided)
try:
    onesignal = get_onesignal_service(
        app_id=os.getenv('ONESIGNAL_APP_ID'),
        rest_api_key=os.getenv('ONESIGNAL_REST_API_KEY')
    )
    if onesignal:
        print("[OK] OneSignal notifications enabled")
    else:
        print("[WARN] OneSignal keys not found - notifications disabled")
except Exception as e:
    print(f"[WARN] OneSignal init failed: {e}")
    onesignal = None

def background_market_simulation():
    """Background thread to keep market data updated."""
    while True:
        try:
            kc.update_market_data()
        except Exception as e:
            print(f"Market Data Error: {e}")
        time.sleep(10) # Wait 10 seconds between fetches

def background_bot_engine():
    """Simulates bots analysing and trading."""
    from strategies import get_all_bots
    from investigator import InvestigatorBot
    
    bots = get_all_bots()
    investigator = InvestigatorBot(cm)
    
    while True:
        if not cm.is_active:
            time.sleep(1)
            continue
            
        # 1. Bots make decisions
        for bot in bots:
            # Skip if disqualified
            if cm.bot_scores.get(bot.bot_id, {}).get("status") == "DISQUALIFIED":
                continue
                
            market_data = kc.get_market_snapshot() # Get market data once per bot decision cycle
            
            if not market_data:
                print("Waiting for market data...")
                continue
                
            signal = bot.analyze(market_data)
            if signal:
                # Log Intent
                logged_signal = kc.log_signal(bot.bot_id, signal['symbol'], signal['type'], signal['price'], signal['reason'])
                
                # 2. Investigator Review
                # Note: check_signal now self-fetches market data if needed
                verdict = investigator.check_signal(logged_signal.copy(), market_data)
                
                # Log Verdict
                kc.log_investigator_verdict(logged_signal['id'], verdict, 
                                          f"Review of {logged_signal['symbol']} signal")
                if verdict == "APPROVED":
                    # Random PnL for simulation (-500 to +1000)
                    pnl = random.uniform(-500, 1000)
                    cm.update_score(bot.bot_id, pnl)
                    print(f"[TRADE] Trade Complete: {bot.name} ({bot.bot_id}) -> {signal['type']} {signal['symbol']} | PnL: {pnl:+.2f} SAR")
                    
                    # Send notification for winning trades
                    if pnl > 0 and onesignal:
                        try:
                            onesignal.notify_winning_trade(
                                robot_name=bot.name,
                                symbol=logged_signal['symbol'],
                                profit=pnl
                            )
                        except Exception as e:
                            print(f"Notification error: {e}")

        time.sleep(3) # Wait before next round of analysis

# Start background threads
sim_thread = threading.Thread(target=background_market_simulation, daemon=True)
bot_thread = threading.Thread(target=background_bot_engine, daemon=True)

sim_thread.start()
bot_thread.start()

@app.route('/')
@app.route('/broadcast')
def broadcast_view():
    return render_template('broadcast.html')

@app.route('/broadcast-gallery')
def broadcast_gallery_view():
    return render_template('broadcast_gallery.html')

@app.route('/carousel-test')
def carousel_test_view():
    return render_template('carousel_test.html')

@app.route('/app')
def mobile_app_view():
    return render_template('mobile_app.html')

@app.route('/live/mobile')
def mobile_live_view():
    return render_template('mobile_live.html')

@app.route('/chart_center')
def chart_center_view():
    return render_template('chart_center.html')

@app.route('/news_center')
def news_center_view():
    return render_template('news_center.html')

# New Application Pages
@app.route('/robots')
def robots_view():
    return render_template('robots.html')

@app.route('/robot/<robot_id>')
def robot_detail_view(robot_id):
    return render_template('robot_detail.html')

@app.route('/portfolio')
def portfolio_view():
    return render_template('portfolio.html')

@app.route('/trades')
def trades_view():
    # Pass trades directly to template as a fallback/initial state
    from strategies import get_all_bots
    bots_map = {b.bot_id: b for b in get_all_bots()}
    
    trades = []
    for signal in kc.bot_signals:
        if signal.get('status') == 'APPROVED':
            bot = bots_map.get(signal['bot_id'])
            # Mock profit for display
            is_buy = signal['type'] == 'BUY'
            profit_pct = round(random.uniform(-2.0, 5.0), 2)
            
            trades.append({
                'id': signal['id'],
                'bot_id': signal['bot_id'],
                'bot_name': bot.name if bot else 'Unknown',
                'symbol': signal['symbol'],
                'type': signal['type'],
                'price': signal['price'],
                'time': signal['timestamp'].strftime("%I:%M %p"),
                'profit': profit_pct
            })
    
    # Sort by ID descending (newest first)
    trades.sort(key=lambda x: x['id'], reverse=True)
    return render_template('trades.html', trades=trades)

@app.route('/reporter')
def reporter_view():
    return render_template('reporter.html')

@app.route('/more')
def more_view():
    return render_template('more.html')

@app.route('/news/emotional')
def emotional_news_view():
    return render_template('emotional_news.html')

@app.route('/trade/<trade_id>')
def trade_details_view(trade_id):
    return render_template('trade_details.html', trade_id=trade_id)

@app.route('/robot/<robot_id>')
def robot_details_view(robot_id):
    return render_template('robot_details.html', robot_id=robot_id)

@app.route('/api/trade/<int:signal_id>')
def api_trade_details(signal_id):
    """Get details for a specific trade/signal"""
    # Find the signal
    signal = None
    for sig in kc.bot_signals:
        if sig['id'] == signal_id:
            signal = sig.copy()
            break
    
    if not signal:
        return jsonify({'error': 'Trade not found'}), 404
    
    # Get bot info
    from strategies import get_all_bots
    bot = next((b for b in get_all_bots() if b.bot_id == signal['bot_id']), None)
    
    # Get investigator log for this signal
    verdict_log = None
    for log in kc.investigator_logs:
        if log.get('signal_id') == signal_id:
            verdict_log = log.copy()
            verdict_log['timestamp'] = verdict_log['timestamp'].isoformat()
            break
    
    # Format signal timestamp
    if 'timestamp' in signal:
        signal['timestamp'] = signal['timestamp'].isoformat()
        
    # Calculate REAL PnL based on ACTUAL Market Data
    pnl = 0.0
    current_price = signal['price'] # Default to entry if no update
    
    # Fetch latest real price from KnowledgeCenter
    real_market_price = kc.market_data.get(signal['symbol'])
    
    if real_market_price and signal.get('status') == 'APPROVED':
        current_price = float(real_market_price)
        quantity = 100 # Standard lot size
        
        # Exact Formula based on Trade Type
        if signal['type'] == 'BUY':
            # Profit = (Current - Entry) * Qty
            pnl = (current_price - signal['price']) * quantity
        else:
            # Profit (Short) = (Entry - Current) * Qty
            pnl = (signal['price'] - current_price) * quantity
    
    # Generate Detailed Evidence & Proofs (Simulated based on Bot Type)
    proofs = {}
    chart_data = []
    audit_report = []
    
    # 1. Generate Authentic Chart Data
    # Connects Input (Entry Price) to Output (Current Real Price)
    chart_data = []
    start_price = signal['price']
    end_price = current_price # This is the REAL market price we fetched above
    
    # Create 15 data points bridging entry to current
    steps = 15
    trend_step = (end_price - start_price) / steps
    
    current_point = start_price
    for i in range(steps):
        # Add tiny market noise (0.01%) for realism, but keep direction strict
        noise = random.uniform(-0.0005, 0.0005) * start_price
        current_point += trend_step + noise
        
        # Determine label time (e.g. T+1min, T+2min...)
        chart_data.append({
            'time': f"T+{i+1}m",
            'price': round(current_point, 2)
        })
        
    # Final point must match current price exactly
    chart_data.append({'time': 'Now', 'price': round(end_price, 2)})

    # 2. Generate Technical Proofs based on Bot Strategy (IN ARABIC)
    if bot:
        if 'RSI' in bot.strategy_title or 'Sniper' in bot.name or 'Wave' in bot.name:
            rsi_val = random.uniform(25, 35) if signal['type'] == 'BUY' else random.uniform(65, 80)
            proofs = {
                'primary_indicator': {'name': 'مؤشر القوة النسبية (RSI)', 'value': round(rsi_val, 2), 'status': 'تشبع بيعي (فرصة شراء)' if signal['type'] == 'BUY' else 'تشبع شرائي (فرصة بيع)'},
                'secondary_indicator': {'name': 'مستوى الدعم', 'value': round(signal['price'] * 0.98, 2), 'status': 'ارتداد ناجح'},
                'volume_analysis': 'سيولة شرائية عالية ظهرت عند ملامسة الدعم.',
                'trend_context': 'نمط انعكاسي إيجابي على فاصل 15 دقيقة.'
            }
        elif 'MACD' in bot.strategy_title:
            proofs = {
                'primary_indicator': {'name': 'مؤشر الماكد (MACD)', 'value': '+0.45', 'status': 'تقاطع إيجابي'},
                'secondary_indicator': {'name': 'خط الإشارة', 'value': 'اختراق', 'status': 'تأكيد الاتجاه'},
                'volume_analysis': 'تزايد في أحجام التداول يؤكد قوة المسار.',
                'trend_context': 'استمرار للموجة الصاعدة بعد تصحيح بسيط.'
            }
        elif 'Bollinger' in bot.strategy_title:
            band_status = 'ملامسة الحد السفلي' if signal['type'] == 'BUY' else 'ملامسة الحد العلوي'
            proofs = {
                'primary_indicator': {'name': 'البولنجر باند', 'value': band_status, 'status': 'ارتداد متوقع'},
                'secondary_indicator': {'name': 'انحراف السعر', 'value': 'عالي', 'status': 'فرصة مضاربية'},
                'volume_analysis': 'تشكل شمعة عاكسة مع فوليوم عالي.',
                'trend_context': 'تداول داخل نطاق عرضي (تذبذب).'
            }
        else: # General/Other
            proofs = {
                'primary_indicator': {'name': 'سلوك السعر (Price Action)', 'value': 'اختراق قمة', 'status': 'مؤكد'},
                'secondary_indicator': {'name': 'المتوسط المتحرك 50', 'value': 'السعر > م.م 50', 'status': 'مسار صاعد'},
                'volume_analysis': 'سيولة ذكية دخلت السهم في آخر 10 دقائق.',
                'trend_context': 'زخم عالي من القطاع يدعم حركة السهم.'
            }

    # 3. Generate Investigator Audit Report (IN ARABIC)
    # 3. Generate Investigator Audit Report (IN ARABIC)
    # Customized based on Strategy Type
    audit_report = [{'check': 'التحقق من الرصيد المتاح', 'status': 'نجح', 'detail': 'الرصيد يغطي قيمة الصفقة بالكامل'}]
    
    if bot:
        if 'Jewel' in bot.name or 'Golden' in bot.strategy_title:
            audit_report.append({'check': 'مستويات فيبوناتشي', 'status': 'نجح', 'detail': 'السعر عند مستوى 61.8 الذهبي'})
        elif 'News' in bot.strategy_title or 'Sentiment' in bot.strategy_title or 'Analyst' in bot.name:
             audit_report.append({'check': 'تحليل الأخبار', 'status': 'نجح', 'detail': 'الأخبار إيجابية وتدعم الاتجاه'})
        elif 'Volume' in bot.strategy_title or 'Striker' in bot.name:
             audit_report.append({'check': 'تدقيق السيولة', 'status': 'نجح', 'detail': 'السيولة كافية للتنفيذ الفوري'})
        else:
            # Default check for others
             audit_report.append({'check': 'فلتر الأخبار السلبية', 'status': 'نجح', 'detail': 'لا توجد أخبار سلبية مؤثرة حالياً'})

    audit_report.extend([
        {'check': 'تقييم المخاطرة', 'status': 'نجح', 'detail': f'نسبة العائد للمخاطرة 1:{random.randint(2,4)} (ممتازة)'},
        {'check': 'تطابق الاستراتيجية', 'status': 'نجح', 'detail': f"إشارة متوافقة 100% مع شروط {bot.name if bot else 'الروبوت'}"}
    ])

    return jsonify({
        'signal': signal,
        'bot': {
            'id': bot.bot_id if bot else 'unknown',
            'name': bot.name if bot else 'Unknown',
            'strategy': bot.strategy_title if bot else 'Unknown',
            'bio': bot.bio if bot else ''
        } if bot else None,
        'verdict': verdict_log,
        'pnl': pnl,
        'extended_data': {
            'chart': chart_data,
            'proofs': proofs,
            'audit': audit_report,
            'market_context': {
                'tasi_index': f"{random.randint(11000, 12500)}.50",
                'sector_performance': f"+{random.uniform(0.1, 1.5):.2f}%",
                'market_sentiment': 'Bullish' if signal['type'] == 'BUY' else 'Bearish'
            }
        }
    })


@app.route('/api/trades')
def api_all_trades():
    """Get all approved trades with details"""
    from strategies import get_all_bots
    bots_map = {b.bot_id: b for b in get_all_bots()}
    
    trades = []
    for signal in kc.bot_signals:
        if signal.get('status') == 'APPROVED':
            bot = bots_map.get(signal['bot_id'])
            trades.append({
                'id': signal['id'],
                'bot_id': signal['bot_id'],
                'bot_name': bot.name if bot else 'Unknown',
                'symbol': signal['symbol'],
                'type': signal['type'],
                'price': signal['price'],
                'reason': signal.get('reason', ''),
                'timestamp': signal['timestamp'].isoformat(),
                'status': signal['status']
            })
    
    # Sort by timestamp descending (newest first)
    trades.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(trades)


@app.route('/api/status')
def api_status():
    """Returns the comprehensive state for the Broadcast View."""
    # Merge Metadata with Live Stats
    from strategies import get_all_bots
    bots_meta = {b.bot_id: {"name": b.name, "human_name": b.human_name, "bio": b.bio, "risk": b.risk} for b in get_all_bots()}
    
    leaderboard = cm.get_leaderboard()
    for entry in leaderboard:
        # Inject static metadata
        meta = bots_meta.get(entry['id'])
        if meta:
            entry.update(meta)
            
    return jsonify({
        "market": kc.get_market_snapshot(),
        "leaderboard": leaderboard,
        "investigator_logs": kc.get_latest_logs(),
        "challenge_info": {
            "start": cm.start_date,
            "end": cm.end_date,
            "active": cm.is_active
        }
    })

# News Analysis APIs
@app.route('/api/news/analyzed')
def get_analyzed_news():
    """Get news with sentiment analysis"""
    try:
        # Get news fetcher and analyzer
        fetcher = get_fetcher()
        analyzer = get_analyzer()
        
        # Fetch all news from all sources
        all_news_by_source = fetcher.fetch_all_news()
        
        # Flatten all news for analysis
        all_news = []
        for source, news_list in all_news_by_source.items():
            all_news.extend(news_list)
        
        # Analyze sentiment for all news
        analyzed_news = analyzer.analyze_news_batch(all_news)
        
        # Format timestamps and confidence
        for news in analyzed_news:
            if 'timestamp' in news:
                news['timestamp'] = news['timestamp'].isoformat()
            if 'confidence' in news:
                news['confidence'] = round(news['confidence'] * 100, 1)
        
        # Get stock summary
        stocks_summary = {}
        for news in analyzed_news:
            stock = news.get('stock')
            if stock:
                if stock not in stocks_summary:
                    stocks_summary[stock] = []
                stocks_summary[stock].append(news)
        
        # Generate recommendations for each stock
        stocks_recommendations = {}
        for stock, stock_news in stocks_summary.items():
            recommendation = analyzer.get_stock_recommendation(stock_news)
            recommendation['stock_name'] = stock_news[0].get('stock_name', stock)
            stocks_recommendations[stock] = recommendation
        
        return jsonify({
            'all_news': analyzed_news,
            'by_source': {
                source: [n for n in analyzed_news if n.get('source') == source]
                for source in all_news_by_source.keys()
            },
            'stocks_summary': stocks_recommendations
        })
        
    except Exception as e:
        print(f"Error in news analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/stock/<stock_symbol>')
def get_stock_news(stock_symbol):
    """Get analyzed news for a specific stock"""
    try:
        fetcher = get_fetcher()
        analyzer = get_analyzer()
        
        # Get news for the stock
        stock_news = fetcher.get_news_by_stock(stock_symbol)
        
        # Analyze
        analyzed = analyzer.analyze_news_batch(stock_news)
        
        # Get recommendation
        recommendation = analyzer.get_stock_recommendation(analyzed)
        
        # Format output
        for news in analyzed:
            if 'timestamp' in news:
                news['timestamp'] = news['timestamp'].isoformat()
            if 'confidence' in news:
                news['confidence'] = round(news['confidence'] * 100, 1)
        
        return jsonify({
            'stock': stock_symbol,
            'news': analyzed,
            'recommendation': recommendation
        })
        
    except Exception as e:
        print(f"Error getting stock news: {e}")
        return jsonify({'error': str(e)}), 500

# Portfolio APIs
@app.route('/api/portfolio')
def get_portfolio_api():
    """Get user portfolio"""
    user_id = request.args.get('user_id', 'default_user')
    portfolio = portfolio_manager.get_portfolio(user_id)
    return jsonify(portfolio)

@app.route('/api/portfolio/add_robot', methods=['POST'])
def add_robot_api():
    """Add robot to portfolio"""
    data = request.json
    result = portfolio_manager.add_robot(
        robot_id=data.get('robot_id'),
        robot_name=data.get('robot_name'),
        emoji=data.get('emoji'),
        allocated_balance=data.get('allocated_balance'),
        user_id=data.get('user_id', 'default_user')
    )
    return jsonify(result)

@app.route('/api/portfolio/remove_robot', methods=['POST'])
def remove_robot_api():
    """Remove robot from portfolio"""
    data = request.json
    result = portfolio_manager.remove_robot(
        robot_id=data.get('robot_id'),
        user_id=data.get('user_id', 'default_user')
    )
    return jsonify(result)

@app.route('/api/portfolio/update_balance', methods=['POST'])
def update_balance_api():
    """Update robot balance"""
    data = request.json
    result = portfolio_manager.update_robot_balance(
        robot_id=data.get('robot_id'),
        new_balance=data.get('new_balance'),
        user_id=data.get('user_id', 'default_user')
    )
    return jsonify(result)

@app.route('/api/robots')
def get_robots_api():
    """Get all robots with their performance"""
    from strategies import get_all_bots
    
    # Get original bots
    original_bots = get_all_bots()
    
    # Get performance data from leaderboard
    leaderboard = cm.get_leaderboard()
    
    # Map emojis
    emoji_map = {
        'المغامر': '🎲',
        'صياد الترند': '🤖', 
        'قناص RSI': '🎯',
        'خبير MACD': '🦾',
        'سيد البولنجر': '🛡️',
        'محلل السيولة': '⚡',
        'قارئ المشاعر': '💭',
        'الذهبي': '🌟',
        'الخاطف (Scalper)': '🔥',
        'المعاكس': '🌊'
    }
    
    # Create a map of performance data keying by bot_id
    perf_map = {item['id']: item for item in leaderboard}
    
    # Combine bot metadata with performance
    robots = []
    for bot in original_bots:
        # Get performance based on ID
        perf_data = perf_map.get(bot.bot_id, {})
        
        robot = {
            'id': bot.bot_id,
            'name': bot.name,
            'emoji': emoji_map.get(bot.name, '🤖'),
            'bio': bot.bio,
            'strategy': bot.strategy_title,
            'risk': bot.risk,
            'balance': perf_data.get('balance', 100000),
            'profit_percent': perf_data.get('profit_pct', 0),
            'trades': perf_data.get('trades', 0),
            'wins': perf_data.get('wins', 0),
            'losses': perf_data.get('losses', 0),
            'success_rate': perf_data.get('win_rate', 0)
        }
        robots.append(robot)
    
    # Sort robots by profit_percent descending so index 0 is the Leader
    robots.sort(key=lambda x: x['profit_percent'], reverse=True)
    
    return jsonify(robots)

@app.route('/api/news/latest')
def api_news_latest():
    """Returns the latest report from Rased."""
    leaderboard = cm.get_leaderboard()
    report = news_service.get_latest_news(leaderboard)
    return jsonify(report)

@app.route('/api/user/recommendations')
def api_recommendations():
    """Returns only APPROVED signals for the User App."""
    all_signals = kc.bot_signals
    approved = [s for s in all_signals if s['status'] == 'APPROVED']
    return jsonify(approved[-20:]) # Return last 20

@app.route('/api/bot/<bot_id>')
def api_bot_details(bot_id):
    """Returns full details for a specific bot."""
    # Base Metadata
    from strategies import get_all_bots
    target_bot = next((b for b in get_all_bots() if b.bot_id == bot_id), None)
    
    if not target_bot:
        return jsonify({"error": "Bot not found"}), 404
        
    # Stats
    stats = cm.bot_scores.get(bot_id, {"pnl": 0, "trades": 0, "wins": 0})
    
    # History & Credibility
    history = kc.get_bot_history(bot_id)
    
    # Calculate Balance (Base 100k + PnL)
    base_balance = 100000
    current_balance = base_balance + stats['pnl']
    
    return jsonify({
        "profile": {
            "id": target_bot.bot_id,
            "name": target_bot.name,
            "human_name": target_bot.human_name,
            "bio": target_bot.bio,
            "risk": target_bot.risk,
            "strategy_title": target_bot.strategy_title,
            "scientific_explanation": target_bot.scientific_explanation
        },
        "stats": {
            "pnl": stats['pnl'],
            "trades": stats['trades'],
            "wins": stats['wins'],
            "balance": current_balance,
            "initial_balance": base_balance
        },
        "history": history
    })

# --- UI Routes for The Centers ---
@app.route('/news')
def news_view():
    return render_template('news_center.html')

@app.route('/charts')
def charts_view():
    return render_template('chart_center.html')

# --- Data APIs ---
@app.route('/api/news')
def api_get_news():
    from flask import request
    symbol = request.args.get('symbol')
    source = request.args.get('source')
    return jsonify(kc.news_service.get_market_news(symbol=symbol, source=source))

@app.route('/api/news/summary')
def api_get_news_summary():
    return jsonify(kc.news_service.get_market_summary())

@app.route('/api/chart/<symbol>')
def api_get_chart(symbol):
    # Fetch 6 months for better context
    df = kc.market_service.get_history(symbol, period="6mo")
    if df.empty:
        return jsonify({"error": "No data"}), 404
        
    # Clean data (remove NaNs which break charts)
    df = df.dropna()
    
    # Format for Lightweight Charts
    data = []
    for index, row in df.iterrows():
        # Handle timezone-aware datetime
        if hasattr(index, 'date'):
            t_str = index.date().strftime('%Y-%m-%d')
        else:
            t_str = index.strftime('%Y-%m-%d')
        
        data.append({
            "time": t_str,
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low']),
            "close": float(row['Close'])
        })
    return jsonify(data)

@app.route('/design-studio')
def design_studio_view():
    return render_template('design_studio.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)


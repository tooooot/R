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
        print("✅ OneSignal notifications enabled")
    else:
        print("⚠️ OneSignal keys not found - notifications disabled")
except Exception as e:
    print(f"⚠️ OneSignal init failed: {e}")
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
    return render_template('trades.html')

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
    
    # Combine bot metadata with performance
    robots = []
    for idx, bot in enumerate(original_bots):
        # Get performance if available
        perf_data = leaderboard[idx] if idx < len(leaderboard) else {}
        
        robot = {
            'id': bot.bot_id,
            'name': bot.name,
            'emoji': emoji_map.get(bot.name, '🤖'),
            'bio': bot.bio,
            'strategy': bot.strategy_title,
            'risk': bot.risk,
            'profit_percent': perf_data.get('profit_pct', 0),
            'trades': perf_data.get('total_trades', 0),
            'success_rate': perf_data.get('win_rate', 0)
        }
        robots.append(robot)
    
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


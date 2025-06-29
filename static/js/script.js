document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // ユーザーのメッセージを表示
        addMessage(message, 'user');
        userInput.value = '';
        userInput.disabled = true; // 入力欄を一時的に無効化
        chatForm.querySelector('button').disabled = true; // 送信ボタンも無効化

        // ローディング表示
        addLoadingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });
            const data = await response.json();
            
            removeLoadingIndicator();
            handleAiResponse(data);
        } catch (error) {
            removeLoadingIndicator();
            addMessage('エラーが発生しました。サーバーが起動しているか確認してください。', 'ai');
            console.error('Error:', error);
        } finally {
            userInput.disabled = false; // 入力欄を再度有効化
            chatForm.querySelector('button').disabled = false; // 送信ボタンも有効化
            userInput.focus();
        }
    });

    function handleAiResponse(data) {
        if (data.type === 'text') {
            // 予定リストJSONが含まれていれば整形して表示
            const eventList = extractEventListFromText(data.content);
            if (eventList.length > 0) {
                addEventListMessage(eventList);
            } else {
                addMessage(data.content, 'ai');
            }
        } else if (data.type === 'delete_candidates') {
            addMessageWithDeleteOptions(data.message, data.content);
        }
    }

    // テキストからJSONイベントリストを抽出
    function extractEventListFromText(text) {
        const eventList = [];
        const regex = /```json([\s\S]*?)```/g;
        let match;
        while ((match = regex.exec(text)) !== null) {
            try {
                const event = JSON.parse(match[1]);
                if (event && event.start_time && event.end_time) {
                    eventList.push(event);
                }
            } catch (e) {}
        }
        return eventList;
    }

    // 予定リストを日本語で整形して表示
    function addEventListMessage(events) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'ai-message');
        let html = '<b>予定リスト</b><ul style="padding-left:1.2em;">';
        events.forEach(event => {
            const start = formatDateTime(event.start_time);
            const end = formatDateTime(event.end_time);
            html += `<li><b>${event.summary || '（タイトルなし）'}</b><br>` +
                `${start} ～ ${end}` +
                (event.location ? `<br>場所: ${event.location}` : '') +
                (event.description ? `<br>説明: ${event.description}` : '') +
                (event.id ? `<br><a href="https://calendar.google.com/calendar/u/0/r/eventedit/${event.id}" target="_blank">Googleカレンダーで開く</a>` : '') +
                '</li>';
        });
        html += '</ul>';
        messageElement.innerHTML = html;
        chatBox.appendChild(messageElement);
        scrollToBottom();
    }

    // 日時を日本語で整形
    function formatDateTime(dt) {
        try {
            const d = new Date(dt);
            return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日 ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
        } catch {
            return dt;
        }
    }

    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.innerHTML = `<p>${message.replace(/\n/g, '<br>')}</p>`;
        chatBox.appendChild(messageElement);
        scrollToBottom();
    }

    function addMessageWithDeleteOptions(message, candidates) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'ai-message');
        
        let html = `<p>${message}</p>`;
        html += '<ul class="delete-candidate-list">';
        candidates.forEach(event => {
            const startTime = new Date(event.start).toLocaleString('ja-JP');
            html += `<li data-event-id="${event.id}">${startTime} - ${event.summary}</li>`;
        });
        html += '</ul>';
        messageElement.innerHTML = html;
        
        chatBox.appendChild(messageElement);
        
        // 削除候補にクリックイベントを追加
        messageElement.querySelectorAll('.delete-candidate-list li').forEach(item => {
            item.addEventListener('click', async () => {
                const eventId = item.dataset.eventId;
                const eventSummary = item.textContent;
                
                addMessage(`「${eventSummary}」の削除を選択しました。`, 'user');
                addLoadingIndicator();

                try {
                    const response = await fetch('/delete_event', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ event_id: eventId }),
                    });
                    const result = await response.json();
                    removeLoadingIndicator();
                    addMessage(result.message || '削除処理が完了しました。', 'ai');
                } catch (error) {
                    removeLoadingIndicator();
                    addMessage('削除中にエラーが発生しました。', 'ai');
                }
            });
        });

        scrollToBottom();
    }
    
    function addLoadingIndicator() {
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('message', 'ai-message');
        loadingElement.id = 'loading';
        loadingElement.innerHTML = '<div class="loading-spinner"></div><span style="margin-left:0.5em;">AIが考え中...</span>';
        chatBox.appendChild(loadingElement);
        scrollToBottom();
    }

    function removeLoadingIndicator() {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // チャット下部にGoogleカレンダー全体を開くボタンを追加（不要なら削除）
    const gcalBtn = document.getElementById('open-gcal-btn');
    if (gcalBtn) {
        gcalBtn.remove();
    }
});

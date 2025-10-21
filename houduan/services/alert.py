"""
异常告警系统

支持邮件和企业微信webhook告警
"""

from __future__ import annotations

import os
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

from ..app import db
from ..models import Message, AIReply


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.email_config = self._load_email_config()
        self.webhook_config = self._load_webhook_config()
        self.alert_history: List[Dict] = []
    
    def _load_email_config(self) -> Optional[Dict]:
        """加载邮件配置"""
        smtp_server = os.environ.get("ALERT_SMTP_SERVER")
        smtp_port = int(os.environ.get("ALERT_SMTP_PORT", "587"))
        username = os.environ.get("ALERT_EMAIL_USERNAME")
        password = os.environ.get("ALERT_EMAIL_PASSWORD")
        to_emails = os.environ.get("ALERT_EMAIL_TO", "").split(",")
        
        if smtp_server and username and password and to_emails:
            return {
                "smtp_server": smtp_server,
                "smtp_port": smtp_port,
                "username": username,
                "password": password,
                "to_emails": [email.strip() for email in to_emails if email.strip()]
            }
        return None
    
    def _load_webhook_config(self) -> Optional[Dict]:
        """加载webhook配置"""
        webhook_url = os.environ.get("ALERT_WEBHOOK_URL")
        webhook_type = os.environ.get("ALERT_WEBHOOK_TYPE", "generic")
        
        if webhook_url:
            return {
                "url": webhook_url,
                "type": webhook_type
            }
        return None
    
    def send_alert(self, title: str, message: str, level: str = "warning", details: Optional[Dict] = None):
        """发送告警"""
        alert_data = {
            "title": title,
            "message": message,
            "level": level,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 记录告警历史
        self.alert_history.append(alert_data)
        
        # 发送邮件告警
        if self.email_config:
            self._send_email_alert(alert_data)
        
        # 发送webhook告警
        if self.webhook_config:
            self._send_webhook_alert(alert_data)
    
    def _send_email_alert(self, alert_data: Dict):
        """发送邮件告警"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config["username"]
            msg['To'] = ", ".join(self.email_config["to_emails"])
            msg['Subject'] = f"[{alert_data['level'].upper()}] {alert_data['title']}"
            
            # 构建邮件内容
            body = f"""
告警时间: {alert_data['timestamp']}
告警级别: {alert_data['level'].upper()}
告警标题: {alert_data['title']}
告警内容: {alert_data['message']}

详细信息:
{json.dumps(alert_data['details'], indent=2, ensure_ascii=False)}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"])
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"邮件告警发送失败: {e}")
    
    def _send_webhook_alert(self, alert_data: Dict):
        """发送webhook告警"""
        try:
            if self.webhook_config["type"] == "wechat":
                # 企业微信格式
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": f"【{alert_data['level'].upper()}】{alert_data['title']}\n{alert_data['message']}\n时间: {alert_data['timestamp']}"
                    }
                }
            else:
                # 通用webhook格式
                payload = {
                    "alert": alert_data,
                    "timestamp": alert_data['timestamp']
                }
            
            response = requests.post(
                self.webhook_config["url"],
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
        except Exception as e:
            print(f"Webhook告警发送失败: {e}")
    
    def check_system_health(self):
        """检查系统健康状态"""
        try:
            # 检查数据库连接
            db.session.execute("SELECT 1")
            db_status = "ok"
        except Exception as e:
            db_status = "error"
            self.send_alert(
                "数据库连接异常",
                f"数据库连接失败: {str(e)}",
                "error",
                {"error": str(e)}
            )
        
        # 检查消息处理异常
        try:
            # 检查最近是否有大量失败的消息
            recent_failed = Message.query.filter(
                Message.status == "failed",
                Message.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            
            if recent_failed > 10:  # 阈值可配置
                self.send_alert(
                    "消息处理异常",
                    f"今日已有 {recent_failed} 条消息处理失败",
                    "warning",
                    {"failed_count": recent_failed}
                )
        except Exception as e:
            print(f"检查消息处理状态失败: {e}")
        
        # 检查AI回复质量
        try:
            # 检查最近AI回复的置信度
            recent_ai_replies = AIReply.query.filter(
                AIReply.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                AIReply.model != "kb"
            ).all()
            
            if recent_ai_replies:
                avg_confidence = sum(r.confidence for r in recent_ai_replies if r.confidence) / len(recent_ai_replies)
                if avg_confidence < 0.5:  # 置信度阈值
                    self.send_alert(
                        "AI回复质量下降",
                        f"最近AI回复平均置信度仅为 {avg_confidence:.2f}",
                        "warning",
                        {"avg_confidence": avg_confidence, "reply_count": len(recent_ai_replies)}
                    )
        except Exception as e:
            print(f"检查AI回复质量失败: {e}")


# 全局告警管理器实例
_alert_manager = None


def get_alert_manager() -> AlertManager:
    """获取告警管理器实例"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def send_alert(title: str, message: str, level: str = "warning", details: Optional[Dict] = None):
    """发送告警的便捷函数"""
    manager = get_alert_manager()
    manager.send_alert(title, message, level, details)


def check_system_health():
    """检查系统健康状态的便捷函数"""
    manager = get_alert_manager()
    manager.check_system_health()

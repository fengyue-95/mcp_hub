import datetime
import subprocess
from mcp.server.fastmcp import FastMCP


class CalendarService:




    def register_tools(self, mcp: FastMCP):

        def execute_applescript(script):
            process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True)
            stdout, stderr = process.communicate()
            return process.returncode == 0, stdout, stderr

        @mcp.tool()
        async def add_calendar_event(title: str, start_time: str, end_time: str = None):
            """
            添加 macOS 日历事件。start_time 格式: '2026-01-30 08:00:00'
            """
            if not end_time:
                dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                end_time = (dt + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

            # 尝试匹配 "Calendar" 或 "日历" (适配中英文系统)
            script = f'''
            tell application "Calendar"
                set targetCal to missing value
                -- 尝试寻找默认日历名
                set calNames to {{"Calendar", "日历", "Work", "工作"}}
                repeat with cName in calNames
                    if exists calendar cName then
                        set targetCal to calendar cName
                        exit repeat
                    end if
                end repeat

                if targetCal is missing value then error "找不到有效的日历列表，请检查名称"

                set start_date to date "{start_time}"
                set end_date to date "{end_time}"
                make new event at targetCal with properties {{summary:"{title}", start date:start_date, end date:end_date}}
            end tell
            '''
            success, out, err = execute_applescript(script)
            if success:
                return f"✅ 成功！已在 macOS 日历中添加: {title}"
            else:
                return f"❌ 失败！错误信息: {err}"

        @mcp.tool()
        async def add_reminder(title: str, due_date: str = None):
            """
            添加 macOS 提醒事项。due_date 格式: '2026-01-30 08:00:00'
            """
            date_clause = f'remind me date:date "{due_date}"' if due_date else ""
            # 尝试匹配 "Reminders" 或 "提醒"
            script = f'''
            tell application "Reminders"
                set targetList to missing value
                set listNames to {{"Reminders", "提醒", "Tasks"}}
                repeat with lName in listNames
                    if exists list lName then
                        set targetList to list lName
                        exit repeat
                    end if
                end repeat

                if targetList is missing value then error "找不到提醒事项列表"

                make new reminder at targetList with properties {{name:"{title}" {"," if due_date else ""} {date_clause}}}
            end tell
            '''
            success, out, err = execute_applescript(script)
            if success:
                return f"🔔 成功！已添加到 macOS 提醒事项"
            else:
                return f"❌ 失败！原因: {err}"
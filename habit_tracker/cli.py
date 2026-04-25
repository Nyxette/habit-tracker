import typer
from rich.console import Console
from db import init_db, get_connection
from datetime import datetime,timedelta
from rich.table import Table
from rich.prompt import Prompt
from apscheduler.schedulers.blocking import BlockingScheduler
from plyer import notification 


app= typer.Typer()
console=Console()


@app.command()
def send_reminder():

    notification.notify(
        title="CLI Habit Tracker Project",
        message="Time to log your habits!!!!!!! RAAAHH",
        timeout=10
    )

@app.command()
def start_reminder(time:str):
    hour,minute=time.split(":")
    scheduler=BlockingScheduler()
    scheduler.add_job(send_reminder,"cron",hour=int(hour),minute=int(minute))
    console.print(f"[green]Reminder set for {time} every day, Press Ctrl+C to stop[/green]")
    scheduler.start()


@app.command()
def menu():
    console.print("[green]Welcome to the Habit Tracker![/green]")
    while True:
        choice=Prompt.ask("Choose an option",choices=["add habit","log habit","stats","show bar graph","list habits","edit habit name","delete a habit","exit"])
        if choice=="add habit":
            name=Prompt.ask("Enter the name of the habit")
            add(name)
        elif choice=="log habit":
            name=Prompt.ask("Enter the name of the habit to log")
            log(name)
        elif choice=="stats":
            name=Prompt.ask("Enter the name of the habit to view stats")
            stats(name)
        elif choice=="show bar graph":
            name=Prompt.ask("Enter the name of the habit to view bar graph")
            show_bars(name)
        elif choice=="list habits":
            list_habits()
        elif choice=="edit habit name":
            old_name=Prompt.ask("Enter the current name of the habit")
            new_name=Prompt.ask("Enter the new name of the habit")
            edit(old_name,new_name)
        elif choice=="delete a habit":
            name=Prompt.ask("Enter the name of the habit to delete")
            delete(name)
        elif choice=="exit":
            console.print("[green]Goodbye![/green]")
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")


@app.command()
def show_bars(habit:str):
    '''show a bar chart yuppee'''
    conn=get_connection()
    cursor=conn.cursor()
    var=cursor.execute("SELECT * from habits where name=?",(habit,)).fetchone()
    if not var:
        console.print(f"[yellow]Habit not found: {habit}[/yellow]")
        conn.close()
        return
    habit_id=var[0]
    dates=cursor.execute("SELECT DISTINCT DATE (logged_at) FROM habit_logs WHERE habit_id=? AND DATE(logged_at)>= ? ORDER BY logged_at DESC",(habit_id, (datetime.now()-timedelta(days=13)))).fetchall()
    logged_dates={row[0] for row in dates}
    for i in range (14):
        date=(datetime.now()-timedelta(days=i)).date().isoformat()
        if date in logged_dates:
            console.print(f"[green]{date}[/green]: [green]█[/green]")
        else:
            console.print(f"[red]{date}[/red]: [red]░[/red]")
    
    conn.close()
        
    


@app.command()
def stats(habit:str):
    """Show stats for habit by name"""
    conn=get_connection()
    cursor=conn.cursor()
    var=cursor.execute("SELECT * from habits where name=?",(habit,)).fetchone()
    if var:
        habit_id=var[0]
        # log_id=cursor.execute("SELECT * from habit_logs where habit_id=?",(habit_id,)).fetchall()
        today=datetime.now().date()

        #Counts of logs in the last week, day and month
        week_ago=(today-timedelta(days=7)).isoformat()
        count_week=cursor.execute("SELECT COUNT(*) from habit_logs where habit_id=? AND DATE(logged_at) >= ?",(habit_id,week_ago)).fetchone()
        day_ago=(today-timedelta(days=1)).isoformat()
        count_day=cursor.execute("SELECT COUNT(*) from habit_logs where habit_id=? AND DATE(logged_at) >= ?",(habit_id,day_ago)).fetchone()
        month_ago=(today-timedelta(days=30)).isoformat()
        count_month=cursor.execute("SELECT COUNT(*) from habit_logs where habit_id=? AND DATE(logged_at) >= ?",(habit_id,month_ago)).fetchone()

        #Checks streaks
        dates = cursor.execute("SELECT DISTINCT DATE (logged_at) FROM habit_logs WHERE habit_id=? ORDER BY logged_at DESC",(habit_id,)).fetchall()
        cur_streak=0
        yesterdate=today
        for i in dates:
            cur_date = datetime.strptime(i[0], "%Y-%m-%d").date()
            if(cur_date==yesterdate):
                cur_streak+=1
                yesterdate=yesterdate-timedelta(days=1)
            else:
                break
        
        
        asc_dates = cursor.execute("SELECT DISTINCT DATE (logged_at) FROM habit_logs WHERE habit_id=? ORDER BY logged_at ASC",(habit_id,)).fetchall()
        current_streak=0
        best_streak=0
        last_date=None
        for i in asc_dates:
            current_date=datetime.strptime(i[0], "%Y-%m-%d").date()
            if (last_date==None or current_date==last_date):
                current_streak+=1
            elif(current_date==last_date+timedelta(days=1)):
                current_streak+=1
            else:
                best_streak=max(best_streak,current_streak)
                current_streak=1
            last_date=current_date
        best_streak=max(best_streak,current_streak)

        table= Table (title="[green]My Habit Table[/green]")
        table.add_column("Habit Name")
        table.add_column("Yesterday")
        table.add_column("Last Week")
        table.add_column("Last Month")
        table.add_column("Current Streak")
        table.add_column("Best Streak")
        table.add_row(habit,str(count_day[0]),str(count_week[0]),str(count_month[0]),str(cur_streak),str(best_streak))
        console.print(table)

    else:
        console.print(f"[yellow]Habit not found: {habit}[/yellow]")
    conn.close()


@app.command()
def log(habit:str):
    """Log a habit by name"""
    conn=get_connection()
    cursor=conn.cursor()
    var=cursor.execute("SELECT * from habits where name=?",(habit,)).fetchone()
    if var:
        console.print(f"[green]Logging habit: {habit}[/green]")
        cursor.execute("INSERT INTO habit_logs (habit_id,logged_at) VALUES (?,?)",(var[0],datetime.now().isoformat()))
    else:
        console.print(f"[yellow]Habit not found: {habit}[/yellow]")
    conn.commit()
    conn.close()

@app.command()
def list_habits():
    """List all habits"""
    conn=get_connection()
    cursor=conn.cursor()
    rows=cursor.execute("SELECT * FROM habits").fetchall()
    for row in rows:
        console.print(f"[cyan]ID:{row[0]}[/cyan], [magenta]Name:{row[1]}[/magenta], Created At:{row[2]}")
    conn.close()

@app.command()
def delete(habit_to_del:str):
    """Delete a habit by its name"""
    conn=get_connection()
    cursor=conn.cursor()
    var=cursor.execute("SELECT * from habits where name=?",(habit_to_del,)).fetchone()
    if var:
        cursor.execute("DELETE from habits where name=?",(habit_to_del,))
        console.print(f"[red]Deleted the habit: {habit_to_del}[/red]")
    else:
        console.print(f"[yellow]Habit not found: {habit_to_del}[/yellow]")
    conn.commit()
    conn.close()

@app.command()
def edit(old_name:str,new_name:str):
    """Edit habit's name"""
    conn=get_connection()
    cursor=conn.cursor()
    var=cursor.execute("SELECT * from habits where name=?",(old_name,)).fetchone()
    if var:
        cursor.execute("UPDATE habits SET name=? where name=?",(new_name,old_name))
        console.print(f"[green]Habit updated: {old_name} -> {new_name}[/green]")
    else:
        console.print(f"[yellow]Habit not found: {old_name}[/yellow]")
    conn.commit()
    conn.close()

@app.command()
def add(name:str):
    """Add a new habit here"""
    console.print(f"[green]Adding habit: {name}[/green]")
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO habits (name,created_at) VALUES (?,?)",(name,datetime.now().isoformat()))
    conn.commit()
    conn.close()

if __name__=="__main__":
    init_db()
    app()
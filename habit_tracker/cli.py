import typer
from rich.console import Console
from db import init_db, get_connection
from datetime import datetime

app= typer.Typer()
console=Console()


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
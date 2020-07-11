from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy import Table, Text
import sqlalchemy
import os

Base = declarative_base()


class HorarioProfesor(Base): 
    __tablename__ = 'horario_profesor'

    id_horario_profesor = Column(Integer, primary_key=True, autoincrement=True)

    id_profesor = Column(Integer, ForeignKey('profesores.id_profesor'))
    id_horario  = Column(Integer, ForeignKey('horarios.id_horario'))

    horario = relationship("Horario", backref="asociar_profesor")
    profesor = relationship("Profesor", backref="asociar_horario")
    __table_args__ = (
       UniqueConstraint('id_profesor', 'id_horario', name='columna_unica'),
    ) 
   
class HorarioCurso(Base):
    __tablename__ = 'horario_curso'
    id_horario_curso = Column(Integer, primary_key=True, autoincrement=True)

    id_curso   = Column(Integer, ForeignKey('cursos.id_curso'))
    id_horario_profesor = Column(Integer, ForeignKey('horario_profesor.id_horario_profesor'))
    
    horario_profesor = relationship("HorarioProfesor", backref="asociar_horario_profesor")
    curso = relationship("Curso", backref="asociar_curso")
    __table_args__ = (
        UniqueConstraint('id_curso', 'id_horario_profesor', name='columna_unica'),
    )
    
class Matricula(Base):
    __tablename__ = 'matricula'
    id_matricula = Column(Integer, primary_key=True, autoincrement=True)
    id_alumno        = Column(Integer, ForeignKey('alumnos.id_alumno'))
    id_horario_curso = Column(Integer, ForeignKey('horario_curso.id_horario_curso'))
    __table_args__ = (
           UniqueConstraint('id_alumno', 'id_horario_curso', name='columna_unica'),
    )
    
    horario_curso = relationship("HorarioCurso", backref="asociar_horario_curso")
    alumnso = relationship("Alumno", backref="asociar_alumno")    
    
class Alumno(Base):
    __tablename__ = "alumnos"
    id_alumno = Column(Integer, primary_key=True, autoincrement=True)
    nombre_alumno   = Column(String(120))
    apellido_alumno = Column(String(120))
    
    horario_curso = relationship("HorarioCurso", secondary="matricula")


  
class Curso(Base):
    __tablename__ = 'cursos'
    id_curso = Column(Integer, primary_key=True, autoincrement=True)
    nombre_curso   = Column(String(120))
    descripcion_curso = Column(String(120))
    
    horario_profesor = relationship("HorarioProfesor", secondary="horario_curso")
    
    
class Profesor(Base):
    __tablename__ = 'profesores'
    id_profesor = Column(Integer, primary_key=True, autoincrement=True)
    nombre_profesor   = Column(String(120))
    apellido_profesor = Column(String(120))
    
    horario = relationship("Horario", secondary="horario_profesor")

class Horario(Base):
    __tablename__ = 'horarios'
    id_horario = Column(Integer, primary_key=True, autoincrement=True)
    
    dia = Column(String(12))
    hora = Column(String(20))

def registrar_profesor():
    nombre = input ("Nombre del profesor: ")
    apellido = input ("Apelido del profesor: ")
    if (nombre!="" and apellido!=""):
        profe = Profesor(nombre_profesor=nombre, apellido_profesor=apellido)
        session.add(profe)
        consulta_horarios = session.query(Horario.id_horario, Horario.dia, Horario.hora)
        for row in consulta_horarios:
            print ("{}-> {} / {}".format(row.id_horario, row.dia, row.hora)) 
        horario = input ("Indique disponibilida para el horario: ")      
        session.add(HorarioProfesor(id_profesor=profe.id_profesor, id_horario=horario))
        session.commit()
    else:
        print ("Debe ingresar todos los campos")    

def registrar_curso():
    consulta_horarios = session.query(Profesor.id_profesor, Profesor.nombre_profesor, Profesor.apellido_profesor, 
                    HorarioProfesor.id_horario_profesor, HorarioProfesor.id_profesor, HorarioProfesor.id_horario,
                    Horario.id_horario, Horario.dia, Horario.hora).\
                    filter(HorarioProfesor.id_profesor==Profesor.id_profesor).\
                    filter(HorarioProfesor.id_horario==Horario.id_horario).\
                    order_by(HorarioProfesor.id_horario_profesor).\
                    all()
    if (len(consulta_horarios)==0):
        input ("Actualmente no hay profesores registrados ... Presione una tecla")
        return

    nombre = input ("Nombre del curso: ")
    descripcion = input ("Descripcion del curso: ")
    if (nombre!="" and descripcion!=""):
        curso = Curso(nombre_curso=nombre, descripcion_curso=descripcion)
        session.add(curso)
        session.commit()
        print ("Porfesores y  Horarios - Disponibles")
        for row in consulta_horarios:
            print ("{} -> {} {} - {} {}".format(
                row.id_horario_profesor,
                row.nombre_profesor,
                row.apellido_profesor,
                row.dia,
                row.hora
        ))
        horario_profesor = input ("Seleccione el profesor para el curso: ")      
        session.add(HorarioCurso(id_curso=curso.id_curso, id_horario_profesor=horario_profesor))
        session.commit()
    else:
        print ("Debe ingresar nombre y descipcion del curso")    

def registrar_alumno():
    consulta_horarios = session.query(HorarioCurso.id_horario_curso,
                                          Curso.nombre_curso,
                                          Profesor.nombre_profesor, Profesor.apellido_profesor, 
                                          Horario.dia, Horario.hora ).\
                            filter(HorarioCurso.id_curso == Curso.id_curso).\
                            filter(HorarioCurso.id_horario_profesor == HorarioProfesor.id_horario_profesor ).\
                            filter(HorarioProfesor.id_profesor == Profesor.id_profesor).\
                            filter(Horario.id_horario == HorarioProfesor.id_horario).\
                            order_by(HorarioCurso.id_horario_curso).\
                            all()
                            
    if (len(consulta_horarios)==0):
        input ("Actualmente no hay cursos registrados ... Presione una tecla")
        return
                            
    nombre   = input ("Nombre del alumno: ")
    apellido = input ("Apellido del alumno: ")
    if (nombre!="" and apellido!=""):
        alumno = Alumno(nombre_alumno=nombre, apellido_alumno=apellido)
        session.add(alumno)
        session.commit()
        print ("Cursos Disponibles")
        

        for row in consulta_horarios:
            print ("{} -> {} - {} {} {} - {}".format(
                row.id_horario_curso,
                row.nombre_curso,
                row.nombre_profesor,
                row.apellido_profesor,
                row.dia,
                row.hora
        ))
        horario_curso = input ("Seleccione el curso a inscribir: ")      
        session.add(Matricula(id_alumno=alumno.id_alumno, id_horario_curso=horario_curso ))
        session.commit()
    else:
        print ("Debe ingresar nombre y descipcion del curso") 

def exportar(data,archivo):
    import json
    import os

    print (data)
    
    #dir = 'D:/'  # También es válido 'C:\\Pruebas' o r'C:\Pruebas'
    file_name = archivo+".json"

    with open(os.path.join(file_name), 'w') as file:
        json.dump(data, file)

engine = create_engine('sqlite:///:memory:')

Base.metadata.create_all(engine)

Session = scoped_session(sessionmaker(bind=engine))        

session = Session()   

lunes      = Horario(dia="Lunes",     hora="08:00 am - 11:30 am")
martes     = Horario(dia="Martes",    hora="09:00 am - 11:00 am")
miercoles  = Horario(dia="Miercoles", hora="01:00 pm - 05:00 pm")
jueves     = Horario(dia="Jueves",    hora="01:00 pm - 04:00 pm")
viernes    = Horario(dia="Viernes",   hora="08:00 am - 12:00 m")
session.add_all([lunes, martes, miercoles,jueves, viernes])
session.commit()

def reporte_profesores():
    print ("Reportes de Profesores")
    print ("---------------------------------------------------------")
    consulta_horarios = session.query(Profesor.id_profesor, Profesor.nombre_profesor, Profesor.apellido_profesor, 
                    HorarioProfesor.id_horario_profesor, HorarioProfesor.id_profesor, HorarioProfesor.id_horario,
                    Horario.id_horario, Horario.dia, Horario.hora).\
                    filter(HorarioProfesor.id_profesor==Profesor.id_profesor).\
                    filter(HorarioProfesor.id_horario==Horario.id_horario).\
                    order_by(HorarioProfesor.id_horario_profesor).\
                    all()
                    
    print ("Porfesores y  Horarios - Disponibles")
    
    lista = []
    for row in consulta_horarios:
        print ("{} -> {} {} - {} {}".format(
            row.id_horario_profesor,
            row.nombre_profesor,
            row.apellido_profesor,
            row.dia,
            row.hora
        )) 
        
        lista.append({'id_horario':row.id_horario_profesor,
                      'nombre_profesor':row.nombre_profesor,
                      'apellido_profesor':row.apellido_profesor,
                      'dia':row.dia,
                      'hora':row.hora})
    exportar(lista,"profesores")

        

       
    input ("Se genero el reporte <<profesores.json>> Presione una tecla para continuar ...")
                   

def reporte_cursos():
    lista = []
    consulta_horarios = session.query(HorarioCurso.id_horario_curso,
        Curso.nombre_curso,
        Profesor.nombre_profesor, Profesor.apellido_profesor, 
        Horario.dia, Horario.hora ).\
        filter(HorarioCurso.id_curso == Curso.id_curso).\
        filter(HorarioCurso.id_horario_profesor == HorarioProfesor.id_horario_profesor ).\
        filter(HorarioProfesor.id_profesor == Profesor.id_profesor).\
        filter(Horario.id_horario == HorarioProfesor.id_horario).\
        order_by(HorarioCurso.id_horario_curso).\
        all()    
    for row in consulta_horarios:
        print ("---------------------------------------------------------")
        print ("{} -> {} - {} {} {} - {}".format(
            row.id_horario_curso,
            row.nombre_curso,
            row.nombre_profesor,
            row.apellido_profesor,
            row.dia,
            row.hora))
        
        lista.append({'id_horario':row.id_horario_curso,
                      'nombre_curso':row.nombre_curso,
                      'nombre_profesor':row.nombre_profesor,
                      'apellido_profesor':row.apellido_profesor,
                      'dia':row.dia,
                      'hora':row.hora})
    exportar(lista,"cursos")
    
    input ("Se genero el reporte <<cursos.json>> Presione una tecla para continuar ...")


def reporte_inscritos():
    print ("Matricula de Alumnos")
    lista = []
    consulta_matricula = session.query(Matricula.id_matricula,Matricula.id_alumno, Matricula.id_horario_curso,
                Alumno.nombre_alumno, Alumno.apellido_alumno,
                Curso.nombre_curso,
                Profesor.nombre_profesor,Profesor.apellido_profesor,
                Horario.dia, Horario.hora).\
                            filter(Matricula.id_alumno == Alumno.id_alumno).\
                            filter(Matricula.id_horario_curso == HorarioCurso.id_horario_curso).\
                            filter(HorarioCurso.id_curso == Curso.id_curso).\
                            filter(HorarioCurso.id_horario_profesor == HorarioProfesor.id_horario_profesor).\
                            filter(HorarioProfesor.id_profesor == Profesor.id_profesor).\
                            filter(HorarioProfesor.id_horario == Horario.id_horario).\
                            order_by(Curso.id_curso).\
                            all()
                            
    for row in consulta_matricula:
        print ("---------------------------------------------------------")
        print ("Alumno: {} {}".format(row.nombre_alumno,row.apellido_alumno))
        print ("Curso: {}".format(row.nombre_curso))
        print ("Profesor: {} {}".format(row.nombre_profesor,row.apellido_profesor))
        print ("Horario: {} {}".format(row.dia,row.hora))
        
        lista.append({'id_alumno':row.id_alumno,
                      'nombre_alumno':row.nombre_alumno,
                      'apellido_alumno':row.apellido_alumno,
                      'nombre_curso':row.nombre_curso,
                      'nombre_profesor':row.nombre_profesor,
                      'apellido_profesor':row.apellido_profesor,
                      'dia':row.dia,
                      'hora':row.hora})
    exportar(lista,"alumnos")

    input ("Se genero el reporte <<alumnos.json>> Presione una tecla para continuar ...")



def menu_principal():
    continuar = True
    while continuar:
        os.system ("cls") 
        print ("1-> Registrar un profesor")
        print ("2-> Registrar un curso")
        print ("3-> Inscribir un Alumno")
        print ("4-> Reporte de profesores")
        print ("5-> Reporte de cursos")
        print ("6-> Reporte de inscritos")
        print ("7-> Salir")
        opcion = input("Seleccione su opción: ")
        if (opcion=='1'):
            registrar_profesor()
        elif (opcion=='2'):
            registrar_curso()
        elif (opcion=='3'):
            registrar_alumno()
        elif (opcion =='4'):
            reporte_profesores()
        elif (opcion =='5'):
            reporte_cursos()
        elif (opcion =='6'):
            reporte_inscritos()
        elif (opcion=='7'):
            continuar = False
        elif (opcion=='8'):
            exportar()

menu_principal()
            


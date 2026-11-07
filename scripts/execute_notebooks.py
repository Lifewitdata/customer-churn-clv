"""Execute plain Python notebook cells in-process without a network kernel.
Supports this project's notebooks (no magics/input). Captures text, tables and plots.
Use Jupyter normally for interactive exploration.
"""
from pathlib import Path
import ast,base64,contextlib,io,os
import nbformat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
os.chdir(root)
for path in sorted((root/'notebooks').glob('*.ipynb')):
    book=nbformat.read(path,as_version=4)
    namespace={'__name__':'__main__'}
    count=0
    for cell in book.cells:
        if cell.cell_type!='code':continue
        count+=1;cell.execution_count=count;cell.outputs=[]
        stream=io.StringIO()
        def capture_plot(*args,**kwargs):
            for num in plt.get_fignums():
                fig=plt.figure(num);buf=io.BytesIO();fig.savefig(buf,format='png',bbox_inches='tight')
                cell.outputs.append(nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode(buf.getvalue()).decode(),'text/plain':'Matplotlib figure'}))
            plt.close('all')
        plt.show=capture_plot
        tree=ast.parse(cell.source)
        expression=tree.body.pop() if tree.body and isinstance(tree.body[-1],ast.Expr) else None
        with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
            exec(compile(tree,str(path),'exec'),namespace)
            if expression is not None:
                value=eval(compile(ast.Expression(expression.value),str(path),'eval'),namespace)
                if value is not None:
                    data={'text/plain':repr(value)}
                    if hasattr(value,'_repr_html_'):
                        html=value._repr_html_()
                        if html:data['text/html']=html
                    cell.outputs.append(nbformat.v4.new_output('execute_result',data=data,execution_count=count))
        if stream.getvalue():cell.outputs.insert(0,nbformat.v4.new_output('stream',name='stdout',text=stream.getvalue()))
    book.metadata['execution_method']='Python AST in-process; all code cells executed, text/table/plot outputs captured'
    nbformat.validate(book);nbformat.write(book,path)
    print('Executed',path.name,flush=True)

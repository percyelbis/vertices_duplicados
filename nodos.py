# Seleccionar la capa deseada
selected_layer = iface.activeLayer()

# Iniciar la edición de la capa
selected_layer.startEditing()

# Crear un campo para almacenar la cantidad de vértices de cada polígono
vertices = 'vertices'
field_type = QVariant.Int
selected_layer.dataProvider().addAttributes([QgsField(vertices, field_type)])

# Crear un campo para almacenar la cantidad total de vértices repetidos de cada polígono
total_repetidos = 'total_repetidos'
field_type = QVariant.Int
selected_layer.dataProvider().addAttributes([QgsField(total_repetidos, field_type)])

selected_layer.updateFields()

# Recorrer los polígonos de la capa
for feature in selected_layer.getFeatures():
    # Obtener la geometría del polígono
    geometry = feature.geometry()
    
    # Obtener la cantidad de vértices del polígono
    vertex_count = geometry.constGet().vertexCount()
    
    # Actualizar el valor del campo 'vertices'
    feature.setAttribute(vertices, vertex_count-1)

    # Obtener la cantidad de vértices repetidos y su frecuencia
    vertex_list = []
    for ring in geometry.asPolygon():
        for point in ring:
            vertex_list.append(point)

    vertex_counts = {}
    for vertex in vertex_list:
        if vertex not in vertex_counts:
            vertex_counts[vertex] = 1
        else:
            vertex_counts[vertex] += 1

    vertex_count_repeated = 0
    for vertex, count in vertex_counts.items():
        if count > 1:
            vertex_count_repeated += count
        
    # Actualizar el valor del campo 'total_repetidos'
    feature.setAttribute(total_repetidos, vertex_count_repeated-2)
    selected_layer.updateFeature(feature)

# Guardar los cambios en la capa
selected_layer.commitChanges()
# Pintar por reglas
rules = ( 
    ('OK', "\"total_repetidos\" = 0", 'green',None), 
    ('REVISAR', " \"total_repetidos\"  > 0", 'red',None)
)
                
layer = iface.activeLayer()
# create a new rule-based renderer
symbol = QgsSymbol.defaultSymbol(layer.geometryType())
renderer = QgsRuleBasedRenderer(symbol)

# get the "root" rule
root_rule = renderer.rootRule()

for label, expression, color_name, scale in rules:
    # create a clone (i.e. a copy) of the default rule
    rule = root_rule.children()[0].clone()
    # set the label, expression and color
    rule.setLabel(label)
    rule.setFilterExpression(expression)
    rule.symbol().setColor(QColor(color_name))

    # append the rule to the list of rules
    root_rule.appendChild(rule)

# delete the default rule
root_rule.removeChildAt(0)

# apply the renderer to the layer
layer.setRenderer(renderer)
# refresh the layer on the map canvas
layer.triggerRepaint()

# Mensaje de éxito
iface.messageBar().pushMessage("Éxito", "Se han actualizado los campos 'vertices' y 'total_repetidos' en la capa " + selected_layer.name(), level=Qgis.Success, duration=20)

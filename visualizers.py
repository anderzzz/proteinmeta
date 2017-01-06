'''Bla bla

'''
from bokeh.embed import components
from bokeh.charts import Bar, output_file, show 
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import Range1d, HoverTool
import pandas as pd
import numpy as np

class Visualizer:
    '''Bla bla

    '''
    def stacked_bars(self, df, x_axis, y_axis, stack, title=None):
        '''Bla bla

        '''
        df_columnwise = df.reset_index()
        df_columnwise[y_axis] = df_columnwise[y_axis].astype(float)
        p = Bar(df_columnwise, label=x_axis, stack=stack, values=y_axis, title=title)
        self.graph_object = p

    def scatter_plot(self, df, x_axis, y_axis, level_name, x_range=None, y_range=None,
                     title=None):
        '''Bla bla

        '''
        df_x = df.xs(x_axis, level=level_name)
        df_y = df.xs(y_axis, level=level_name)
        index_ids = df_x.index.values
        index_ids_string = ['-'.join(point_name) for point_name in index_ids]
        x_data = df_x.values
        y_data = df_y.values

        source = ColumnDataSource(data=dict(
                                  x = x_data, y = y_data,
                                  desc = index_ids_string,))
        hover = HoverTool(tooltips=[('(x,y)','(@x, @y)'),
                                   ('desc','@desc')])
        p = figure(tools=[hover])
        p.circle('x', 'y', size=10, source=source)
        self.graph_object = p

    def spider_plot(self, df, dims, same_level_norm=False, common_range=None):
        '''Bla bla

        '''
        if not dims in df.index.names:
            raise KeyError('Dimension with name %s not found in data' %(dims))
        else:
            levels = df.index.levels[df.index.names.index(dims)]
            n_legs = len(levels)

        # Compute angles of bars
        angles = [x * 2.0 * np.pi / len(levels) for x in range(0, n_legs)]

        # Compute ranges of each bar
        axis_ranges = []
        level_data = []
        for level in levels:
            df_level = df.xs(level, level=dims)
            level_max = df_level.max()
            level_min = df_level.min()
            axis_ranges.append((level_min, level_max))
            level_data.append(df_level)
        n_webs = len(level_data[0])

        max_of_max = max([axis_range[1] for axis_range in axis_ranges])
        min_of_min = min([axis_range[0] for axis_range in axis_ranges])
        if same_level_norm:
            axis_ranges = [(min_of_min, max_of_max)] * n_legs

        if not common_range is None:
            axis_ranges_new = []
            for axis_range in axis_ranges:
                if axis_range[0] < common_range[0] or \
                   axis_range[1] > common_range[1]:
                    raise ValueError('Common range for spider plot does ' + \
                          'not contain data of range ' + \
                          '%s to %s' %(str(axis_range[0]), str(axis_range[1])))
                else:
                    axis_range_new = common_range
                axis_ranges_new.append(axis_range_new)
            axis_ranges = axis_ranges_new

        # Translate data into xy-coordinates for plot
        point_coords = []
        for data, axis_range, angle in zip(level_data, axis_ranges, angles):
            line_coords_x = []
            line_coords_y = []
            for data_point in data:
                radial = (data_point - axis_range[0]) / (axis_range[1] - axis_range[0])
                x = radial * np.sin(angle)
                y = radial * np.cos(angle)
                line_coords_x.append(x)
                line_coords_y.append(y)
            point_coords.append([line_coords_x, line_coords_y])

        # Resort the xy-coordinates according to convention by plotting program
        data_to_plot = {}
        for xy in [0, 1]:
            line_data = []
            for line in range(0, n_webs):
                points = list(range(0, n_legs)) + [0]
                point_data = []
                for point in points:
                    point_data.append(point_coords[point][xy][line])
                line_data.append(point_data)
            data_to_plot[xy] = line_data

        # Create axis line
        base_line = [0.0, 1.1 * max_of_max]
        axis_to_plot = {}
        for angle in angles:
            x = base_line[0] * np.cos(angle) + base_line[1] * np.sin(angle)
            y = base_line[0] * np.sin(angle) + base_line[1] * np.cos(angle)
            coord_x = axis_to_plot.setdefault(0, [])
            coord_y = axis_to_plot.setdefault(1, [])
            coord_x.append([0.0, x])
            coord_y.append([0.0, y])
            axis_to_plot[0] = coord_x
            axis_to_plot[1] = coord_y

        p = figure()
        p.multi_line(data_to_plot[0], data_to_plot[1], alpha=0.6)
        p.multi_line(axis_to_plot[0], axis_to_plot[1], color='black',
                     line_width=2.0)

        # Hide grid and axes
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.axis.visible = False

        self.graph_object = p 

    def make_html(self, fileout_path):
        '''Bla bla

        '''
        output_file(fileout_path)
        show(self.graph_object)

    def make_components(self, fileout_path):
        '''Bla bla

        '''
        script, div = components(self.graph_object)
        with open(fileout_path + '_div', 'w') as fout:
            fout.write(div)
        with open(fileout_path + '_script', 'w') as fout:
            fout.write(script)

    def __init__(self, legend='top_right'):
        '''Bla bla

        '''
        self.legend = legend

        self.graph_object = None

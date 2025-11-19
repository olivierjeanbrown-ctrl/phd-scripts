% =========================================================================
% Data Generator GUI
% Author: Olivier Brown
% Description:
%   MATLAB GUI application that allows users to generate, visualize,
%   and export simulated datasets. The user specifies the number of 
%   groups, sample sizes, means, and standard deviations. The script 
%   then generates normally distributed data and exports it to Excel.
%
% Course: Graduate MATLAB Programming (Final Project)
% Dependencies: None (uses built-in MATLAB UI components)
% =========================================================================

function datagenerator

% -------------------------------------------------------------------------
% GUI: Main Figure
% -------------------------------------------------------------------------
dataselect = figure(1);
set(dataselect, 'Name', 'Data Generator', ...
    'NumberTitle', 'Off', ...
    'Position', [400 400 800 500]);

titletext = text(.27,1,'Data Generator', 'FontSize', 24);
axis off

% User input: number of groups
datacreatorcondition = uicontrol('Style', 'edit', ...
    'Position', [300 340 150 20]);

labelcondition = uicontrol('Style', 'text', ...
    'String', 'Enter number of groups.', ...
    'Position', [300 360 150 20]);

buttoncondition = uicontrol('Style', 'pushbutton', ...
    'String', 'Continue', ...
    'Position', [300 320 150 20], ...
    'Callback', @variables);



% =========================================================================
% Step 1 — Group Specification
% =========================================================================
function variables(~, ~)

numofconditions = str2double(get(datacreatorcondition,'String'));

if isnan(numofconditions)
    msgbox('Invalid input. Please enter a numeric value.', ...
        'Warning', 'error');
    return
end

% Hide earlier GUI elements
set(datacreatorcondition,'Visible','off');
set(labelcondition,'Visible','off');
set(buttoncondition,'Visible','off');

% Prepare cell arrays
nboxes = {};
muboxes = {};
sdboxes = {};
grouplabel = {};

% Labels
labeln = uicontrol('Style', 'text', ...
    'String', 'Enter N', ...
    'Position', [40 300 150 20]);

labelmu = uicontrol('Style', 'text', ...
    'String', 'Enter mean', ...
    'Position', [40 280 150 20]);

labelsd = uicontrol('Style', 'text', ...
    'String', 'Enter SD', ...
    'Position', [40 260 150 20]);

xoffset = [0 0 0 0];

% Create edit boxes for each group
for cycle = 1:numofconditions

    nboxes{cycle} = uicontrol('Style', 'edit', ...
        'Position', [200 300 50 20] + xoffset);

    muboxes{cycle} = uicontrol('Style', 'edit', ...
        'Position', [200 280 50 20] + xoffset);

    sdboxes{cycle} = uicontrol('Style', 'edit', ...
        'Position', [200 260 50 20] + xoffset);

    grouplabel{cycle} = uicontrol('Style', 'text', ...
        'Position', [200 330 50 20] + xoffset, ...
        'String', cycle);

    xoffset = xoffset + [100 0 0 0];
end

% Button to compute data
datacreatorcompute = uicontrol('Style', 'pushbutton', ...
    'String', 'Generate data', ...
    'Position', [300 200 150 30], ...
    'Callback', @compute);



% =========================================================================
% Step 2 — Generate and Organize Data
% =========================================================================
function compute(~, ~)

n = zeros(1,numofconditions);
mu = zeros(1,numofconditions);
sd = zeros(1,numofconditions);

% Validate inputs
for i = 1:numofconditions

    if isempty(get(nboxes{i},'String')) || ...
       isempty(get(muboxes{i},'String')) || ...
       isempty(get(sdboxes{i},'String'))

        msgbox('All fields must be filled.', 'Warning', 'error');
        return
    end

    if isnan(str2double(get(nboxes{i},'String'))) || ...
       isnan(str2double(get(muboxes{i},'String'))) || ...
       isnan(str2double(get(sdboxes{i},'String')))

        msgbox('Invalid character detected. Please enter numbers only.', ...
            'Warning', 'error');
        return
    end

    n(i)  = str2double(get(nboxes{i},'String'));
    mu(i) = str2double(get(muboxes{i},'String'));
    sd(i) = str2double(get(sdboxes{i},'String'));
end

% Generate data
rawdatacombined = {};
for g = 1:numofconditions
    data = randn(n(g),1) .* sd(g) + mu(g);
    rawdatacombined = [rawdatacombined; num2cell(data)];
end

% Organize data
rawdataorganized = {};
for p = 1:length(rawdatacombined)
    rawdataorganized = [rawdataorganized; {p, rawdatacombined{p}}];
end

% Assign group labels
group = zeros(sum(n),1);
checkpoint = 1;
for g = 1:numofconditions
    group(checkpoint:checkpoint + n(g) - 1) = g;
    checkpoint = checkpoint + n(g);
end

groupcell = num2cell(group);
rawdatawithgroups = [groupcell, rawdataorganized];

headers = {'IV', 'Participant', 'DV'};
rawdatafinal = [headers; rawdatawithgroups];

% Clean GUI
delete(labelmu); delete(labeln); delete(labelsd);
delete(labelcondition); delete(datacreatorcompute);

for g = 1:numofconditions
    set(muboxes{g}, 'Visible','off');
    set(nboxes{g}, 'Visible','off');
    set(sdboxes{g}, 'Visible','off');
    set(grouplabel{g}, 'Visible','off');
end

% File naming UI
desiredfilename = uicontrol('Style', 'edit', ...
    'Position', [240 360 300 20], ...
    'String', 'Enter file name (without ".xls")');

desiredfilenamebutton = uicontrol('Style', 'pushbutton', ...
    'String', 'Save', ...
    'Position', [300 340 150 20], ...
    'Callback', @filesaveprocedure);



% =========================================================================
% Step 3 — File Saving Logic
% =========================================================================
function filesaveprocedure(~, ~)

invalidfilechars = {'.',',','!','@','#','$','%', ...
    '^','&','*','{','}','/','|','\','''','"', ...
    '=',';',':','<','>','?',' ','(',')'};

filename = get(desiredfilename,'String');

if isempty(filename)
    msgbox('Please enter a filename.', 'Warning', 'error');
    return
elseif contains(filename, invalidfilechars)
    msgbox('Filename contains invalid characters.', 'Warning', 'error');
    return
end

finalname = strcat(filename, '.xls');

% File exists?
if isfile(finalname)
    set(desiredfilename,'Visible','off');
    set(desiredfilenamebutton,'Visible','off');

    uicontrol('Style','text', ...
        'Position',[300 380 250 20], ...
        'String','File exists. Override?');

    uicontrol('Style', 'pushbutton', ...
        'String', 'No', ...
        'Position', [300 340 250 20], ...
        'Callback', @cancelbuttonpress);

    uicontrol('Style', 'pushbutton', ...
        'String', 'Yes', ...
        'Position', [300 360 250 20], ...
        'Callback', @commitbuttonpress);

else
    writecell(rawdatafinal, finalname);
    close all;
end
end


% Cancel
function cancelbuttonpress(~, ~)
    uicontrol('Style','text', ...
        'String','Cancelling...', ...
        'Position',[300 300 150 20]);
    pause(2);
    close all;
end

% Override
function commitbuttonpress(~, ~)
    uicontrol('Style','text', ...
        'String','Overriding...', ...
        'Position',[300 280 150 20]);
    pause(1);

    finalname = strcat(get(desiredfilename,'String'),'.xls');
    delete(finalname);
    writecell(rawdatafinal, finalname);

    close all;
end

end % compute
end % variables
end % main
